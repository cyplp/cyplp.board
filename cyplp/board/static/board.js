document.addEventListener("DOMContentLoaded", function(event) {
    var addItems = document.querySelectorAll('.addItem');

    for (var item = 0, len=addItems.length; item < len; item++)
	{
	    addItems[item].addEventListener('click', function(e) {eventAddItems(e)});
	}

    var items = document.querySelectorAll('.item');
    for (var item=0, len=items.length; item<len; item++)
	{
	    items[item].addEventListener('dragstart', function(event){
		var column = event.target.parentNode.dataset.column;

		event.dataTransfer.effectAllowed = "move";
		event.dataTransfer.setData("text", event.target.id);
		event.dataTransfer.setData("from", column);
								 });
	}

    var columns = document.querySelectorAll('.column');
    var boardId = document.getElementById('board').dataset.board;

    for(var item=0, len=columns.length; item<len; item++)
	{
	    columns[item].addEventListener('drop', function(event){

		event.preventDefault();
		var id = event.dataTransfer.getData("text");
		var from =  event.dataTransfer.getData("from");


		var to;
		if (event.target.className == 'column')
		    {
			to = event.target.dataset.column;
		    }
		else
		    {
			to = event.target.parentNode.dataset.column;
		    }
		var target = event.target;

		var req = new XMLHttpRequest();
		req.open("POST", "/board/"+boardId+"/move/"+id.split("-")[1], true);
		req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
		req.onreadystatechange = function () { if (req.readyState != 4 || req.status != 200) return;
						       console.log("Success: " + req.responseText); };
		req.send(JSON.stringify({from: from, to:to}));


		if (target.className=="column"){
		    target.appendChild(document.getElementById(id))
		}
		else{

		    if (target.parentNode.className == "column")
			{
			    target.parentNode.appendChild(document.getElementById(id))
			}
		}


	    });
	    columns[item].addEventListener('dragover', function(e){
	     							   e.preventDefault();});
	}

    var title = document.getElementById('title-board');
    title.addEventListener('click', function(event){
	var req = new XMLHttpRequest();
	req.open("GET", "/board/"+boardId+"/title", true);
	req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
	req.onreadystatechange = function () {
	    if (req.readyState != 4 || req.status != 200) return;
	    event.target.parentNode.outerHTML = req.responseText;
	};

	req.send();
    });

    var columnTitles = document.querySelectorAll('.column-title');
    for(var item=0, len=columnTitles.length; item<len; item++)
	{
	    columns[item].addEventListener('click',
					   function(event){
					       column = event.target.parentNode.parentNode.dataset.column;
					       var req = new XMLHttpRequest();
					       req.open("GET", "/board/"+boardId+"/column/"+column+"/title", true);
					       req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
					       req.onreadystatechange = function () {
						   if (req.readyState != 4 || req.status != 200) return;
						   event.target.parentNode.outerHTML = req.responseText;
					       };

	req.send();
					   });
	}
  });

function eventAddItems(evt)
    {

	node = evt.currentTarget;

	form = document.getElementById('addItem-'+node.dataset.column);
	form.style.display = 'block';

	node.parentNode.parentNode.style.display = 'none' ;
    }
