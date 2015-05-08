document.addEventListener("DOMContentLoaded", function(event) {
    var addItems = document.querySelectorAll('.addItem');

    for (var item = 0, len=addItems.length; item < len; item++)
	{
	    addItems[item].addEventListener('click', function(event) {eventAddItems(event)});
	}

    var items = document.querySelectorAll('.item');
    for (var item=0, len=items.length; item<len; item++)
	{
	    items[item].addEventListener('dragstart', function(event){dragstart(event);});
	}

    var columns = document.querySelectorAll('.column');
    var boardId = document.getElementById('board').dataset.board;

    for(var item=0, len=columns.length; item<len; item++)
	{
	    columns[item].addEventListener('drop', function(event){drop(event)});
	    columns[item].addEventListener('dragover', function(event){event.preventDefault();});
	}

    var title = document.getElementById('title-board');
    title.addEventListener('click', function(event){clickBoardTitle(event)});

    var columnTitles = document.querySelectorAll('.column-title');
    for(var item=0, len=columnTitles.length; item<len; item++)
	{
	    columnTitles[item].addEventListener('click', function(event){clickColumnTitle(event)});
	}


    var itemTitles = document.querySelectorAll('.item-title');
    for(var item=0, len=itemTitles.length; item<len; item++)
    {
    	var child = itemTitles[item].firstChild;

    	if (child.hasChildNodes() == false)
    	    {
    		itemTitles[item].addEventListener('click',
    					       function(event){
						   var itemId = event.target.parentNode.parentNode.id.split('-')[1];
						   var boardId = document.getElementById('board').dataset.board;

						   var req = new XMLHttpRequest();
						   req.open("GET", "/board/"+boardId+"/edit/"+itemId+"/title", true);
						   req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
						   req.onreadystatechange = function () {
						   if (req.readyState != 4 || req.status != 200) return;

						   event.target.parentNode.outerHTML = req.responseText;
						   var close = document.getElementById('close');
						   close.addEventListener('click', function(event) {location.reload()});
						   var deleteButton = document.getElementById('delete');
						   deleteButton.addEventListener('click', function(event) {deleteItem(event, itemId, boardId);});
						   };

						   req.send();
    					       });
    	    }

    }
  });

function eventAddItems(evt){
	var node = evt.currentTarget;

	var form = document.getElementById('addItem-'+node.dataset.column);
	form.style.display = 'block';
	form.querySelectorAll('.input')[0].autofocus = "on";
	node.parentNode.parentNode.style.display = 'none' ;
    }

function dragstart(event){
    var column = event.target.parentNode.dataset.column;

    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData("text", event.target.id);
    event.dataTransfer.setData("from", column);
}


function drop (event){
    event.preventDefault();
    var id = event.dataTransfer.getData("text");
    var from =  event.dataTransfer.getData("from");
    var boardId = document.getElementById('board').dataset.board;
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


}

function clickBoardTitle(event){
    var boardId = document.getElementById('board').dataset.board;

    var req = new XMLHttpRequest();
    req.open("GET", "/board/"+boardId+"/title", true);
    req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    req.onreadystatechange = function () {
	if (req.readyState != 4 || req.status != 200) return;
	event.target.parentNode.outerHTML = req.responseText;
    };

    req.send();
}

function clickColumnTitle(event){
    var column = event.target.parentNode.parentNode.dataset.column;
    var boardId = document.getElementById('board').dataset.board;

    var req = new XMLHttpRequest();
    req.open("GET", "/board/"+boardId+"/column/"+column+"/title", true);
    req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    req.onreadystatechange = function () {
	if (req.readyState != 4 || req.status != 200) return;
	event.target.parentNode.outerHTML = req.responseText;
    };

    req.send();
}

function deleteItem(event, itemId, boardId){
    var req = new XMLHttpRequest();

    req.open("DELETE", "/board/"+boardId+"/delete/"+itemId, true);
    req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    req.onreadystatechange = function () {
	if (req.readyState != 4 || req.status != 200) return;
	location.reload();
    }
    req.send();
}
