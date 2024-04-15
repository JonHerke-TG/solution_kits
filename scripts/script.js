import { globSync } from "glob";
import { parse } from "yaml";
import fs from "fs";
import path from "path";
import "dotenv/config";
import AWS from "aws-sdk";
import mime from "mime";
import zlib from "zlib";
import { renderMarkdown } from "./markdown.js";

const bucketName = "tigergraph-solution-kits";
const disableCacheControl = "max-age=0,no-cache,no-store";
const imageCacheControl = "max-age=86400"; // cache image for  1 day

const s3 = new AWS.S3();
const commonBucketConfig = {
  Bucket: bucketName,
};

async function syncFile(file, cacheControl = disableCacheControl) {
  const params = {
    ...commonBucketConfig,
    Key: file,
    Body: fs.readFileSync(file),
    ContentType: mime.getType(path.extname(file)),
    CacheControl: cacheControl,
  };

  let shouldUpload = true;
  try {
    const object = await s3
      .headObject({
        Bucket: bucketName,
        Key: file,
      })
      .promise();
    const length = object.ContentLength;
    const fileLength = params.Body.length;

    if (length === fileLength) {
      shouldUpload = false;
    }
  } catch (error) {
    if (error.code === "NotFound") {
    } else {
      shouldUpload = false;
    }
  }

  console.log(file, shouldUpload);
  if (shouldUpload) {
    try {
      const data = await s3.upload(params).promise();
      console.log(`${file} => ${data.Location}`);
      return data.Location;
    } catch (error) {
      console.error(`Error uploading ${file}:`, error);
    }
  }

  return `https://${bucketName}.s3.us-west-1.amazonaws.com/${file}`;
}

async function syncFolder(folder, cacheControl = disableCacheControl) {
  const files = globSync([`${folder}/*`, `${folder}/*/*`]);
  let results = [];
  for (let file of files) {
    if (fs.lstatSync(file).isDirectory()) {
      continue;
    }
    results.push(await syncFile(file, cacheControl));
  }
  return results;
}

async function syncPattern(pattern, cacheControl = disableCacheControl) {
  const files = globSync(pattern);
  let results = [];
  for (let file of files) {
    results.push(await syncFile(file, cacheControl));
  }
  return results;
}

function getAllSolutions() {
  const metaFiles = globSync("**/meta/meta.yml", {
    ignore: ["solution_kits/scripts/**"],
  });

  return metaFiles.map((file) => file.slice(0, -"/meta/meta.yml".length));
}

async function getSolution(dir) {
  console.log("\n\nProcessing", dir, "...");
  const file = fs.readFileSync(`${dir}/meta/meta.yml`, "utf8");
  const content = parse(file);

  let iconPath = "";
  if (fs.existsSync(`${dir}/meta/icon.png`)) {
    iconPath = `${dir}/meta/icon.png`;
  } else if (fs.existsSync(`${dir}/meta/icon.jpg`)) {
    iconPath = `${dir}/meta/icon.jpg`;
  }

  if (iconPath) {
    content.metadata.icon = await syncFile(iconPath);
  }

  content.metadata.images = await syncFolder(`${dir}/meta/images`, imageCacheControl);
  content.metadata.images.sort();

  content.metadata.insightsApplications = await syncPattern(`${dir}/meta/Insights*.json`);

  content.metadata.provider = content.metadata.provider || "TigerGraph";
  content.metadata.algorithms = content.metadata.algorithms || [];

  await syncFolder(`${dir}/data`);

  // We assume the model and doc folders contains markdown files
  await syncFolder(`${dir}/model`);
  await syncFolder(`${dir}/doc`);

  const markdownFiles = globSync([`${dir}/model/**/*.md`, `${dir}/doc/**/*.md`]);
  const htmlFiles = [];
  for (let markdownFile of markdownFiles) {
    const html = renderMarkdown(dir, markdownFile);
    const htmlFile = markdownFile.replace(".md", ".html");

    const params = {
      ...commonBucketConfig,
      Key: htmlFile,
      Body: html,
      ContentType: "text/html",
      CacheControl: disableCacheControl,
    };

    try {
      const data = await s3.upload(params).promise();
      console.log(`${htmlFile} => ${data.Location}`);
      htmlFiles.push(data.Location);
    } catch (error) {
      console.error("Error uploading html file:", error);
      process.exit(1);
    }
  }

  content.metadata.docLinks = htmlFiles;
  return content;
}

function concatFiles(files) {
  const fileContents = files.map((file) => fs.readFileSync(file, "utf8"));

  let content = "";
  for (let i = 0; i < files.length; i++) {
    content += "#File: " + files[i] + "\n";
    content += fileContents[i];
    content += "\n\n";
  }

  return content;
}

async function getSolutionDetail(dir, first, last) {
  const schemaFiles = globSync(`${dir}/schema/*.gsql`);
  const schema = concatFiles(schemaFiles);

  let schemaJSON = "";
  try {
    schemaJSON = fs.readFileSync(`${dir}/meta/schema.json`, "utf8");
  } catch (error) {}
  let styleJSON = "";
  try {
    styleJSON = fs.readFileSync(`${dir}/meta/style.json`, "utf8");
  } catch (error) {}

  const queryFiles = globSync([`${dir}/queries/*.gsql`, `${dir}/queries/*/*.gsql`]);

  const firstFiles = [];
  for (let file of first) {
    const path = `${dir}/queries/${file}`;
    if (queryFiles.includes(path)) {
      firstFiles.push(path);
    }
  }
  const lastFiles = [];
  for (let file of last) {
    const path = `${dir}/queries/${file}`;
    if (queryFiles.includes(path)) {
      lastFiles.push(path);
    }
  }
  const middleFiles = queryFiles.filter(
    (file) => !firstFiles.includes(file) && !lastFiles.includes(file)
  );

  const allQueryFiles = [...firstFiles, ...middleFiles, ...lastFiles];
  const query = concatFiles(allQueryFiles);

  const sampleLoadingJobFiles = globSync(`${dir}/loading_job/*.gsql`);
  const sampleLoadingJob = concatFiles(sampleLoadingJobFiles);

  const resetFiles = globSync(`${dir}/reset/*.gsql`);
  const reset = concatFiles(resetFiles);

  let queriesDocs = "";
  try {
    queriesDocs = JSON.parse(
      fs.readFileSync(`${dir}/meta/metadata_descriptor.json`, "utf8")
    ).queries;
  } catch (error) {}

  const hasUDF = fs.existsSync(`${dir}/udfs`);

  return {
    schema,
    schemaJSON: schemaJSON ? JSON.parse(schemaJSON) : undefined,
    styleJSON: styleJSON ? JSON.parse(styleJSON) : undefined,
    queriesDocs: queriesDocs ? queriesDocs : [],

    query,
    sampleLoadingJob,
    reset,
    hasUDF,
  };
}

async function main() {
  const solutions = getAllSolutions();
  const metadataList = [];
  for (let solution of solutions) {
    const { metadata, queries: { first = [], last = [] } = {} } = await getSolution(solution);

    metadataList.push({
      ...metadata,
      path: solution,
    });

    const solutionDetails = await getSolutionDetail(solution, first, last);
    const params = {
      ...commonBucketConfig,
      Key: `${solution}/meta.json`,
      Body: zlib.gzipSync(JSON.stringify(solutionDetails)),
      ContentType: "application/json",
      CacheControl: disableCacheControl,
      ContentEncoding: "gzip",
    };

    try {
      const data = await s3.upload(params).promise();
      console.log(`${solution}/meta.json => ${data.Location}`);
    } catch (error) {
      console.error(`Error uploading ${solution}:`, error);
      process.exit(1);
    }
  }

  const params = {
    ...commonBucketConfig,
    Key: "list.json",
    Body: zlib.gzipSync(JSON.stringify(metadataList)),
    ContentType: "application/json",
    CacheControl: disableCacheControl,
    ContentEncoding: "gzip",
  };

  try {
    const data = await s3.upload(params).promise();
    console.log(`list.json => ${data.Location}`);
  } catch (error) {
    console.error("Error uploading solution list:", error);
    process.exit(1);
  }

  try {
    const data = await s3
      .upload({
        ...commonBucketConfig,
        Key: "favicon.ico",
        Body: fs.readFileSync("scripts/favicon.ico"),
        ContentType: mime.getType(path.extname("scripts/favicon.ico")),
        CacheControl: imageCacheControl,
      })
      .promise();
    console.log(`favicon.json => ${data.Location}`);
  } catch (error) {
    console.error("Error uploading favicon:", error);
    process.exit(1);
  }
}

main();

// Debug code
// function decodeSolution(path) {
//   const file = fs.readFileSync(path, "utf8");
//   const content = JSON.parse(file);
//   const { schema, query, sampleLoadingJob, reset } = content;
//   console.log(schema);
//   console.log(query);
//   console.log(sampleLoadingJob);
//   console.log(reset);
// }
