document.addEventListener("DOMContentLoaded", function(event) {
    console.log("DOM fully loaded and parsed");

    var addItems = document.querySelectorAll('.addItem');

    for (var item = 0, len=addItems.length; item < len; item++)
	{
	    addItems[item].addEventListener('click', function(e) {eventAddItems(e)});
	}

    var items = document.querySelectorAll('.item');
    for (var item=0, len=items.length; item<len; item++)
	{
	    items[item].addEventListener('dragstart', function(e){
								  e.dataTransfer.effectAllowed = "move";
								  e.dataTransfer.setData("text", e.target.id);
								 });
	}

    var columns = document.querySelectorAll('.column');
    for(var item=0, len=columns.length; item<len; item++)
	{
	    columns[item].addEventListener('drop', function(event){
		console.log('drop');
		event.preventDefault();
		id = event.dataTransfer.getData("text");

		target = event.target;
		if (target.class="column"){
		    target.appendChild(document.getElementById(id))
		}
	    });
	    columns[item].addEventListener('dragover', function(e){
	     							   e.preventDefault();});
	}
  });

function eventAddItems(evt)
    {
	console.log("clicked !");
	node = evt.currentTarget;
	console.log(node.dataset.column);

	form = document.getElementById('addItem-'+node.dataset.column);
	form.style.display = 'block';

	node.parentNode.parentNode.style.display = 'none' ;
    }
