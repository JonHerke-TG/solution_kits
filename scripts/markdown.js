import fs from 'fs'
import { basename, extname } from 'path';
import { marked } from 'marked';

function capitalize(s)
{
    return s[0].toUpperCase() + s.slice(1);
}

function normalizeName(name) {
  return name.split('_').map(name => capitalize(name)).join(' ');
}

export function renderMarkdown(solution, file) {
    const content = fs.readFileSync(file, { encoding: 'utf8' })

    // Convert Markdown to HTML
    const htmlContent = marked(content);

    // Wrap the HTML content with the necessary HTML and CSS
    const htmlTemplate = `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <link rel="icon" type="image/svg+xml"  sizes="any" href="/favicon.ico" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />    
        <title>TigerGraph - ${normalizeName(basename(solution, extname(solution)))} - ${normalizeName(basename(file, extname(file)))}</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-light.css">
        <style>
            .markdown-body {
                box-sizing: border-box;
                min-width: 200px;
                max-width: 980px;
                margin: 0 auto;
                padding: 45px;
            }
        
            @media (max-width: 767px) {
                .markdown-body {
                    padding: 15px;
                }
            }
        </style>        
      </head>
      <body>
        <article class="markdown-body">
          ${htmlContent}
        </article>
      </body>
    </html>
  `;

    return htmlTemplate;
}