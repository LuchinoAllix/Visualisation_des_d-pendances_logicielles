let treesData = [];
let currentTreeIndex = 0;	

const width = document.querySelector('.tree-container').clientWidth;
const height = 500;

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
	.style("fill", d => d.data.level);

}

function loadFiles() {
	const type = document.getElementById("type-select").value;
    const category = document.getElementById("category-select").value;

	const filePath = `trees\\paths_${category}_${type}.json`;

	document.getElementById("css-link").href =`trees\\colors_${category}.css`
	fetch(filePath)
    .then(response => response.json())
    .then(paths => {
      const treeFiles = paths.map(path => fetch(path).then(response => response.json()));
      return Promise.all(treeFiles);
    })
    .then(data => {
		d3.select("svg").remove();
		treesData = data;
		const slider = document.getElementById("tree-slider");
          slider.max = treesData.length;
          slider.value = 1;
          currentTreeIndex = 0;
          drawTree(treesData[currentTreeIndex]);
          document.getElementById('filename').innerHTML = `
            <div>Fichier n&deg ${currentTreeIndex}</div>
            <div>Version GitHub : ${treesData[currentTreeIndex].dir}</div>
            <div>Date de release : ${treesData[currentTreeIndex].date}</div>`;
		document.getElementById('generalData').innerHTML = `
		<div>Nombre de versions : ${treesData[currentTreeIndex].nbVersion}</div>
            <div>Nombre Maximum de commits : ${treesData[currentTreeIndex].maxCommit}</div>
            <div>Nombre Maximum de contributeurs: ${treesData[currentTreeIndex].maxContributors}</div>`;
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
        <div>Fichier n&deg ${currentTreeIndex}</div>
        <div>Version GitHub : ${treesData[currentTreeIndex].dir}</div>
        <div>Date de release : ${treesData[currentTreeIndex].date}</div>`;
		document.getElementById('generalData').innerHTML = `
		<div>Nombre de versions : ${treesData[currentTreeIndex].nbVersion}</div>
		<div>Nombre Maximum de commits : ${treesData[currentTreeIndex].maxCommit}</div>
		<div>Nombre Maximum de contributeurs: ${treesData[currentTreeIndex].maxContributors}</div>`;
    }
  });

document.getElementById("type-select").addEventListener("change", loadFiles);
document.getElementById("category-select").addEventListener("change", loadFiles);

document.addEventListener("DOMContentLoaded", () => {
	loadFiles();
  });