package org.apache.giraph.io.formats;

import java.util.Iterator;

import org.apache.giraph.graph.Vertex;
import org.apache.giraph.conf.DefaultImmutableClassesGiraphConfigurable;
import org.apache.giraph.conf.GiraphConfiguration;
import org.apache.giraph.conf.ImmutableClassesGiraphConfiguration;
import org.apache.giraph.edge.ByteArrayEdges;
import org.apache.giraph.edge.Edge;
import org.apache.giraph.edge.MutableEdge;
import org.apache.giraph.edge.MutableEdgesIterable;
import org.apache.giraph.edge.MutableEdgesWrapper;
import org.apache.giraph.edge.MutableOutEdges;
import org.apache.giraph.edge.OutEdges;
import org.apache.giraph.edge.StrictRandomAccessOutEdges;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;

public class LabelPropagationVertex extends DefaultImmutableClassesGiraphConfigurable<LongWritable, LongWritable, NullWritable>
	implements Vertex<LongWritable, LongWritable, NullWritable>{

	 /** Vertex id. */
	  private LongWritable id;
	  /** Vertex value. */
	  private LongWritable value;
	  /** Outgoing edges. */
	  private OutEdges<LongWritable, NullWritable> edges;
	  /** If true, do not do anymore computation on this vertex. */
	  private boolean halt;
	  
	  
	@Override
	public void addEdge(Edge<LongWritable, NullWritable> edge) {
		edges.add(edge);
	}
	
	@Override
	public Iterable<NullWritable> getAllEdgeValues(LongWritable targetVertexId) {
		return null;
	}
	
	@Override
	public NullWritable getEdgeValue(LongWritable targetVertexId) {
		return NullWritable.get();
	}
	
	@Override
	public Iterable<Edge<LongWritable, NullWritable>> getEdges() {
		return edges;
	}
	
	@Override
	public LongWritable getId() {
		return id;
	}
	
	@Override
	public Iterable<MutableEdge<LongWritable, NullWritable>> getMutableEdges() {
		  // If the OutEdges implementation has a specialized mutable iterator,
	    // we use that; otherwise, we build a new data structure as we iterate
	    // over the current edges.
	    if (edges instanceof MutableOutEdges) {
	      return new Iterable<MutableEdge<LongWritable, NullWritable>>() {
	        @Override
	        public Iterator<MutableEdge<LongWritable, NullWritable>> iterator() {
	          return ((MutableOutEdges<LongWritable, NullWritable>) edges).mutableIterator();
	        }
	      };
	    } else {
	      return new MutableEdgesIterable<LongWritable, NullWritable>(this);
	    }
	}
	
	@Override
	public int getNumEdges() {
		return edges.size();
	}
	
	@Override
	public LongWritable getValue() {
		return value;
	}
	
	@Override
	public void initialize(LongWritable id, LongWritable value) {
		this.id = id;
		this.value = value;
		this.edges = new ByteArrayEdges<LongWritable, NullWritable>();
		
	}
	@Override
	public void initialize(LongWritable id, LongWritable value,
			Iterable<Edge<LongWritable, NullWritable>> edges) {
		this.id = id;
		this.value = value;
		setEdges(edges);
	}
	
	@Override
	public boolean isHalted() {
		return halt;
	}
	
	@Override
	public void removeEdges(LongWritable targetVertexId) {
		edges.remove(targetVertexId);
	}
	
	@Override
	public void setEdgeValue(LongWritable targetVertexId, NullWritable edgeValue) {
		// If the OutEdges implementation has a specialized random-access
	    // method, we use that; otherwise, we scan the edges.
	    if (edges instanceof StrictRandomAccessOutEdges) {
	      ((StrictRandomAccessOutEdges<LongWritable, NullWritable>) edges).setEdgeValue(
	          targetVertexId, edgeValue);
	    } else {
	      for (MutableEdge<LongWritable, NullWritable> edge : getMutableEdges()) {
	        if (edge.getTargetVertexId().equals(targetVertexId)) {
	          edge.setValue(edgeValue);
	        }
	      }
	    }
	}
	
	@Override
	public void setEdges(Iterable<Edge<LongWritable, NullWritable>> edges) {
	    // If the iterable is actually an instance of OutEdges,
	    // we simply take the reference.
	    // Otherwise, we initialize a new OutEdges.
	    if (edges instanceof OutEdges) {
	      this.edges = (OutEdges<LongWritable, NullWritable>) edges;
	    } else {
	    	GiraphConfiguration gc = new GiraphConfiguration();
	    	gc.setOutEdgesClass(ByteArrayEdges.class);
	    	ImmutableClassesGiraphConfiguration<LongWritable, LongWritable, NullWritable> immutableClassesGiraphConfiguration = new ImmutableClassesGiraphConfiguration<>(gc);
	    	this.edges = immutableClassesGiraphConfiguration.createOutEdges();
	    	this.edges.initialize(edges);
	    }
	}
	
	@Override
	public void setValue(LongWritable value) {
		this.value = value;
	}
	
	@Override
	public void unwrapMutableEdges() {
		  if (edges instanceof MutableEdgesWrapper) {
		      edges = ((MutableEdgesWrapper<LongWritable, NullWritable>) edges).unwrap();
		    }
	}
	
	@Override
	public void voteToHalt() {
	    halt = true;
	}
	
	@Override
	public void wakeUp() {
	    halt = false;
	}


}
