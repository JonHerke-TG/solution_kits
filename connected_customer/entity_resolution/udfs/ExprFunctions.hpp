/******************************************************************************
 * Copyright (c) 2015-2016, TigerGraph Inc.
 * All rights reserved.
 * Project: TigerGraph Query Language
 * udf.hpp: a library of user defined functions used in queries.
 *
 * - This library should only define functions that will be used in
 *   TigerGraph Query scripts. Other logics, such as structs and helper
 *   functions that will not be directly called in the GQuery scripts,
 *   must be put into "ExprUtil.hpp" under the same directory where
 *   this file is located.
 *
 * - Supported type of return value and parameters
 *     - int
 *     - float
 *     - double
 *     - bool
 *     - string (don't use std::string)
 *     - accumulators
 *
 * - Function names are case sensitive, unique, and can't be conflict with
 *   built-in math functions and reserve keywords.
 *
 * - Please don't remove necessary codes in this file
 *
 * - A backup of this file can be retrieved at
 *     <tigergraph_root_path>/dev_<backup_time>/gdk/gsql/src/QueryUdf/ExprFunctions.hpp
 *   after upgrading the system.
 *
 ******************************************************************************/

#ifndef EXPRFUNCTIONS_HPP_
#define EXPRFUNCTIONS_HPP_

#include <stdlib.h>
#include <stdio.h>
#include <string>
#include <gle/engine/cpplib/headers.hpp>
#include <algorithm>
#include <iostream>
/**     XXX Warning!! Put self-defined struct in ExprUtil.hpp **
 *  No user defined struct, helper functions (that will not be directly called
 *  in the GQuery scripts) etc. are allowed in this file. This file only
 *  contains user-defined expression function's signature and body.
 *  Please put user defined structs, helper functions etc. in ExprUtil.hpp
 */
#include "ExprUtil.hpp"

namespace UDIMPL {
  typedef std::string string; //XXX DON'T REMOVE

  /****** BIULT-IN FUNCTIONS **************/
  /****** XXX DON'T REMOVE ****************/
  inline int64_t str_to_int (string str) {
    return atoll(str.c_str());
  }

  inline int64_t float_to_int (float val) {
    return (int64_t) val;
  }

  inline string to_string (double val) {
    char result[200];
    sprintf(result, "%g", val);
    return string(result);
  }

  inline int64_t levenshtein_distance(string s1, string s2){
  int len_s1 = s1.length();
  int len_s2 = s2.length();
  int dist[len_s1+1][len_s2+1];

  int i;
  int j;
  int len_cost;

  for (i = 0;i <= len_s1;i++)
  {
      dist[i][0] = i;
  }
  for(j = 0; j<= len_s2; j++)
  {
      dist[0][j] = j;
  }
  for (i = 1;i <= len_s1;i++)
  {
      for(j = 1; j<= len_s2; j++)
      {
          if( s1[i-1] == s2[j-1] )
          {
              len_cost = 0;
          }
          else
          {
              len_cost = 1;
          }
          dist[i][j] = std::min(
          dist[i-1][j] + 1,                  // delete
          std::min(dist[i][j-1] + 1,         // insert
          dist[i-1][j-1] + len_cost)           // substitution
        );
       if( (i > 1) &&
       (j > 1) &&
       (s1[i-1] == s2[j-2]) &&
       (s1[i-2] == s2[j-1])
       )
       {
       dist[i][j] = std::min(
       dist[i][j],
        dist[i-2][j-2] + len_cost   // transposition
       );
       }
   }}
 return dist[len_s1][len_s2];
 }

  inline double jaroDistance(string a, string b)
  { 
    // Register strings length.
    int aLength(a.size());
    int bLength(b.size());
    
    // If one string has null length, we return 0.
    if (aLength == 0 || bLength == 0)
    {
        return 0.0;
    }
    
    // Calculate max length range.
    int maxRange(std::max(0, std::max(aLength, bLength) / 2 - 1));
    
    // Creates 2 vectors of integers. 
    std::vector<bool> aMatch(aLength, false);
    std::vector<bool> bMatch(bLength, false);
    
    // Calculate matching characters.
    int matchingCharacters(0);
    for (int aIndex(0); aIndex < aLength; ++aIndex)
    {   
        // Calculate window test limits (limit inferior to 0 and superior to bLength).
        int minIndex(std::max(aIndex - maxRange, 0));
        int maxIndex(std::min(aIndex + maxRange + 1, bLength));
        
        if (minIndex >= maxIndex)
        {   
            // No more common character because we don't have characters in b to test with characters in a.
            break;
        }
        
        for (int bIndex(minIndex); bIndex < maxIndex; ++bIndex)
        {   
            if (!bMatch.at(bIndex) && a.at(aIndex) == b.at(bIndex))
            {   
                // Found some new match.
                aMatch[aIndex] = true;
                bMatch[bIndex] = true;
                ++matchingCharacters;
                break;
            }
        }
    }

    // If no matching characters, we return 0.
    if (matchingCharacters == 0)
    {
        return 0.0;
    }
        
    // Calculate character transpositions.
    std::vector<int> aPosition(matchingCharacters, 0);
    std::vector<int> bPosition(matchingCharacters, 0);
    
    for (int aIndex(0), positionIndex(0); aIndex < aLength; ++aIndex)
    {
        if (aMatch.at(aIndex))
        {
            aPosition[positionIndex] = aIndex;
            ++positionIndex;
        }   
    }       
        
    for (int bIndex(0), positionIndex(0); bIndex < bLength; ++bIndex)
    {   
        if (bMatch.at(bIndex))
        {
            bPosition[positionIndex] = bIndex;
            ++positionIndex;
        }   
    }       
        
    // Counting half-transpositions.
    int transpositions(0);
    for (int index(0); index < matchingCharacters; ++index)
    {
        if (a.at(aPosition.at(index)) != b.at(bPosition.at(index)))
        {
            ++transpositions;
        }
    }       
        
    // Calculate Jaro distance.
    return (
        JARO_WEIGHT_STRING_A * matchingCharacters / aLength +
        JARO_WEIGHT_STRING_B * matchingCharacters / bLength +
        JARO_WEIGHT_TRANSPOSITIONS * (matchingCharacters - transpositions / 2) / matchingCharacters
    );  
  }

  inline double jaroWinklerDistance(string a, string b){
    double distance(jaroDistance(a, b));
    if (distance > JARO_WINKLER_BOOST_THRESHOLD)
        {   
            int commonPrefix(0);
            for (int index(0), indexEnd(std::min(std::min(a.size(), b.size()), JARO_WINKLER_PREFIX_SIZE)); index < indexEnd; ++index)
                {       
                    if (a.at(index) == b.at(index))
                        {
                            ++commonPrefix;
                        }
                    else    
                        {
                            break;
                        }
                }       
         
            distance += JARO_WINKLER_SCALING_FACTOR * commonPrefix * (1.0 - distance);
        }
    return distance;
  }

  inline void copy_vertex (VERTEX& tgt, VERTEX src){
    tgt = src;
  }
}
/****************************************/

#endif /* EXPRFUNCTIONS_HPP_ */

