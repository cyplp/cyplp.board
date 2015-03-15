document.addEventListener("DOMContentLoaded", function(event) {
    console.log("DOM fully loaded and parsed");

    var addItems = document.querySelectorAll('.addItem');

    for (var item = 0, len=addItems.length; item < len; item++)
	{
	    addItems[item].addEventListener('click', function(e) {eventAddItems(e)});
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
