/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
 
package org.apache.giraph.examples;
 
import org.apache.giraph.graph.BasicComputation;
import org.apache.giraph.graph.Vertex;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.log4j.Logger;

import java.io.IOException;

import java.util.*;

import org.apache.giraph.edge.Edge;


/**
 * Demonstrates a basic Pregel label propagation implementation.
 */
@Algorithm(name = "Label propagation", description = "Sets the value of each vertex to the a label signifying its assigned community")
public class SimpleLabelPropagationComputation
        extends
        BasicComputation<LongWritable, LongWritable, NullWritable, LongWritable> {
 
    /** Number of supersteps for this test */
    public static final int MAX_SUPERSTEPS = 30;
      
    /** Class logger */
    private static final Logger LOG = Logger
            .getLogger(SimpleLabelPropagationComputation.class);
 
    @Override
    public void compute(
            Vertex<LongWritable, LongWritable, NullWritable> vertex,
            Iterable<LongWritable> messages) throws IOException {
        
        
        // Set value to id in the first superstep and propagate results
        if (getSuperstep() == 0) {
            LOG.info(vertex.getId() + ": SuperStep: " + getSuperstep() + ": Value " + vertex.getId() + "\n");
            vertex.setValue(vertex.getId());
            sendMessageToAllEdges(vertex, vertex.getId());
        }
        
        // if superstep is not the first and less than the MAX_SUPERSTEPS proceed
        else if ((getSuperstep() != 0)  && (getSuperstep() < MAX_SUPERSTEPS)) {
            
            LOG.info(vertex.getId() + ": SuperStep: " + getSuperstep() + ": Value " + vertex.getValue());
            
            // create list from messages
            List<Long> result = new ArrayList<>();
            for (LongWritable message : messages) {
                result.add(message.get());
              }
            
            // if there is only one element, set the community to the smallest value
            if (result.size() == 1) {
                LOG.info("Received Value: " + result.get(0) + " Current Value " + vertex.getValue().get());
                if (result.get(0) < vertex.getValue().get()){
                    LOG.info("Vertex_value: " + vertex.getValue() + " New_vertex_value:" + result.get(0) );
                    vertex.setValue(new LongWritable(result.get(0)));
                    sendMessageToAllEdges(vertex, vertex.getId());
                }
                LOG.info("\n\n");
            } 
            
            else if (result.size() == 0){
                vertex.voteToHalt();
            }
            else {
                // Create frequency map
                Long current_min  = (long) 999999;
                Integer max_freq = 0;
                Set<Long> distinct = new HashSet<>(result);
                for (Long s: distinct) {
                    Integer freq = Collections.frequency(result, s);

                    
                    // If the number of neihgbors having a label is bigger than the current one
                    // assign the max_freq and current min to the one found
                    if (freq > max_freq) {
                        max_freq = freq;
                        current_min = s;
                    }
                    
                    if ((freq == max_freq) && (s < current_min)) {
                        current_min = s;
                    }
                }
                LOG.info("Messages: " + result);
                LOG.info("Community:" + current_min + " freq: " + max_freq);
                        
                // if vertex value changes propagate
                if (!vertex.getValue().equals(new LongWritable(current_min))) {
                    LOG.info("Vertex_value: " + vertex.getValue() + " New_vertex_value:" + current_min + "\n\n");
                    vertex.setValue(new LongWritable(current_min));
                    sendMessageToAllEdges(vertex, vertex.getValue());
                } else {
                    LOG.info("\n\n");
                }
            }
        } else {
            vertex.voteToHalt(); 
            } 

    }

}
