package org.apache.giraph.io.formats;

import java.io.IOException;
import java.util.ArrayList;

import org.apache.giraph.graph.Vertex;
import org.apache.giraph.io.formats.TextVertexInputFormat;
import org.apache.giraph.edge.Edge;
import org.apache.giraph.edge.EdgeFactory;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.InputSplit;
import org.apache.hadoop.mapreduce.TaskAttemptContext;

public class LabelPropagationInputFormat extends TextVertexInputFormat<LongWritable, LongWritable, NullWritable>{


	@Override
	public TextVertexReader createVertexReader(
			InputSplit split, TaskAttemptContext context) throws IOException {
		return new ComponentisationVertexReader();
	}

	public class ComponentisationVertexReader extends TextVertexReader {

		@Override
		public boolean nextVertex() throws IOException, InterruptedException {
			return getRecordReader().nextKeyValue();
		}
		
		@Override
		public Vertex<LongWritable, LongWritable, NullWritable> getCurrentVertex() throws IOException, InterruptedException {
			Text line = getRecordReader().getCurrentValue();
			String[] parts = line.toString().split(" ");
			LongWritable id = new LongWritable(Long.valueOf(parts[0]));
			ArrayList<Edge<LongWritable, NullWritable>> edgeIdList = new ArrayList<Edge<LongWritable, NullWritable>>();
			 
			if(parts.length > 1) {
				for (int i = 1; i < parts.length; i++) {
					Edge<LongWritable, NullWritable> edge = EdgeFactory.create(new LongWritable(Long.valueOf(parts[i])));
					edgeIdList.add(edge);
				}
			}
		    Vertex<LongWritable, LongWritable, NullWritable> vertex = new LabelPropagationVertex();
		    vertex.initialize(id, new LongWritable(0L), edgeIdList);
		    return vertex;
		}

}

}
