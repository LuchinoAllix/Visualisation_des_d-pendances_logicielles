let treesData = [];
let currentTreeIndex = 0;	

const width = document.querySelector('.tree-container').clientWidth;
const height = 500;
const tooltip = d3.select(".tooltip");

function drawTree(treeData){

	// Dimension (bottom vaut 100 pour compenser le text et le gradient au dessus)
	const margin = {top: 10, right: 10, bottom: 100, left: 10},
			width = window.innerWidth - margin.left - margin.right,
			height = window.innerHeight - margin.top - margin.bottom;

	// création de l'objet treemap
	const treemap = d3.tree().size([width,height]);

	// Création de la hierarchie
	let nodes = d3.hierarchy(treeData, d => d.children);
	nodes = treemap(nodes);

	// ajoute l'objet à la page html
	const svg = d3.select(".tree-container")
				.append("svg")
				.attr("width", "100%")
				.attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
				.attr("preserveAspectRatio", "xMidYMid meet");
						
	const g = svg.append("g")
				.attr("transform","translate(" + margin.left + "," + margin.top + ")");

	const link = g.selectAll(".link")
				.data(nodes.descendants().slice(1))
				.enter().append("line")
				.attr("class", "line")
				.style("stroke", d => d.data.level)
				.attr("x1", d => d.x)
				.attr("y1", d => d.y)
				.attr("x2", d => d.parent.x)
				.attr("y2", d => d.parent.y);

	// adds each node as a group
	const node = g.selectAll(".node")
					.data(nodes.descendants())
					.enter().append("g")
					.attr("class", d => "node" + (d.children ? " node--internal" : " node--leaf"))
					.attr("transform", d => "translate(" + d.x + "," + d.y + ")");

	// adds the circle to the node
	node.append("circle")
	.attr("r", 0.1)
	.style("stroke", d => d.data.type)
	.style("fill", d => d.data.level)
	.on("mouseover", (d) => {
		tooltip.transition().duration(200).style("opacity", .9);
		tooltip.html("Name: " + d.data.name + "<br/>");
	})
	.on("mouseout", d => {
		tooltip.transition().duration(500).style("opacity", 0);
	});

	// adds the text to the node
	/*
	node.append("text")
	.attr("dy", ".35em")
	.attr("x", d => d.children ? (d.data.value + 5) * -1 : d.data.value + 5)
	.attr("y", d => d.children && d.depth !== 0 ? -(d.data.value + 5) : d)
	.style("text-anchor", d => d.children ? "end" : "start")
	.text(d => d.data.name);*/

}

function loadFiles() {
	fetch('paths.json')
	  .then(response => response.json())
	  .then(paths => {
		const treeFiles = paths.map(path => fetch(path).then(response => response.json()));
		return Promise.all(treeFiles);
	  })
	  .then(data => {
		treesData = data;
		drawTree(treesData[currentTreeIndex]);
	  })
	  .catch(error => console.error('Error fetching or processing tree files:', error));
  }

  // Slider functionality
  const slider = document.getElementById("tree-slider");
  slider.addEventListener("input", () => {
    const index = parseInt(slider.value) - 1;
    if (index !== currentTreeIndex) {
      currentTreeIndex = index;
      d3.select("svg").remove(); 
      drawTree(treesData[currentTreeIndex]);
      document.getElementById('filename').innerHTML = `
        <span>Tree number : ${currentTreeIndex}</span>
        <span>date : ${treesData[currentTreeIndex].date}</span>
        <span>dir : ${treesData[currentTreeIndex].dir}</span>
        <span>version npm : ${treesData[currentTreeIndex].version}</span>`;
    }
  });

loadFiles();