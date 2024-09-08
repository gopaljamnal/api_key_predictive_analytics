import React, { useState } from "react";
import axios from "axios";
import { DataSet, Network } from "vis-network/standalone/umd/vis-network.min.js";
import { ProgressBar } from "react-bootstrap";
import 'bootstrap/dist/css/bootstrap.min.css'; // Import bootstrap styles
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [uploading, setUploading] = useState(false); // Track the uploading status
  const [progress, setProgress] = useState(0); // Progress value (0 - 100)

  // Handle file selection
  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  // Handle file upload and call the API
  const handleUpload = async () => {
    if (!file) {
      alert("Please select a PDF file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true); // Start showing the progress bar

    try {
      // Simulate progress
      setProgress(20);

      const response = await axios.post("http://127.0.0.1:5000/upload_pdf", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percentCompleted);
        },
      });

      setProgress(60); // Set progress after upload completion
      console.log(response);

      const { entities, relationships } = response.data;
      const nodes = entities.map((entity, index) => ({
        id: index + 1,
        label: entity.text,
        group: entity.label, // Grouping by entity type for styling
      }));

      const edges = relationships.map((rel) => {
        const fromNode = nodes.find((node) => node.label === rel.from);
        const toNode = nodes.find((node) => node.label === rel.to);
        if (fromNode && toNode) {
          return {
            from: fromNode.id,
            to: toNode.id,
            label: rel.relation, // Display the relationship on the edge
            arrows: "to", // Arrow pointing to the target
          };
        }
        return null;
      }).filter(edge => edge !== null);

      setProgress(80); // Simulate delay before graph rendering

      setGraphData({ nodes, edges });
      renderGraph({ nodes, edges });

      setProgress(100); // Completion
      setTimeout(() => setUploading(false), 500); // Delay hiding the progress bar slightly
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Error uploading file or extracting data.");
      setUploading(false); // Hide progress bar on error
    }
  };

  // Function to render the graph using Vis.js with force-directed physics
  const renderGraph = (graphData) => {
    const container = document.getElementById("network");

    const data = {
      nodes: new DataSet(graphData.nodes),
      edges: new DataSet(graphData.edges),
    };

    const options = {
      physics: {
        enabled: true,
        barnesHut: {
          gravitationalConstant: -2000, // Controls clustering
          centralGravity: 0.3,
          springLength: 200, // Edge length
          springConstant: 0.05,
        },
        stabilization: {
          enabled: true,
          iterations: 1000, // How long to stabilize the graph
        },
      },
      interaction: {
        hover: true, // Enable hover to highlight nodes and edges
      },
      nodes: {
        shape: 'dot',
        size: 20,
        font: {
          size: 14,
          color: "#333"
        },
        borderWidth: 2,
        shadow: true, // Adding shadow for better visualization
      },
      edges: {
        width: 2,
        font: {
          align: "middle", // Relationship label position
          size: 12,
        },
        arrows: {
          to: { enabled: true, scaleFactor: 1.2 }, // Arrowhead styling
        },
        color: {
          color: "#848484",
          highlight: "#848484",
          hover: "#848484",
        },
        smooth: true, // Smooth edges for aesthetic effect
      },
      groups: {
        PERSON: { color: { background: "#97C2FC", border: "#2B7CE9" } },
        ORG: { color: { background: "#FFA07A", border: "#FA8072" } },
        GPE: { color: { background: "#90EE90", border: "#32CD32" } },
        // Add more entity types with custom colors as needed
      },
    };

    const network = new Network(container, data, options);
     network.on("stabilizationIterationsDone", function () {
       // Disable physics after stabilization
       network.setOptions({physics: false});
     });
  };

  return (
    <div className="App">
      <h1>Knowledge Graph from PDF</h1>

      {/* File upload input */}
      <input type="file" onChange={handleFileChange} />

      {/* Upload button */}
      <button onClick={handleUpload} disabled={uploading}>
        {uploading ? "Uploading..." : "Upload PDF"}
      </button>

      {/* Progress bar */}
      {uploading && <ProgressBar now={progress} label={`${progress}%`} animated />}

      {/* Network container for the graph */}
      <div id="network" style={{ height: "600px", border: "1px solid lightgray" }}></div>
    </div>
  );
}

export default App;
