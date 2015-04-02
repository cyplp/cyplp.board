document.addEventListener("DOMContentLoaded", function(event) {
    console.log("DOM fully loaded and parsed");
    var editContent = document.getElementById('edit-content');
    editContent.addEventListener('click', function(e) {editForm(e)});
});

function editForm(event){
    console.log("heeeeee");
    var boardId = event.target.parentNode.parentNode.dataset.board;
    var itemId = event.target.parentNode.parentNode.dataset.item;
    var req = new XMLHttpRequest();
    req.open("GET", "/board/"+boardId+"/edit/"+itemId+"/content", true);
    req.onreadystatechange = function () {
	if (req.readyState != 4 || req.status != 200)
	    {
		return
	    };
	event.target.parentNode.parentNode.outerHTML = req.responseText;
	};
    req.send()
}
