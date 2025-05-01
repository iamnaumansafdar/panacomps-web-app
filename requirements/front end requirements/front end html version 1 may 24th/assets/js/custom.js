// Get the modal
var modal = document.getElementById("viewDwtailModal");
var btn = document.getElementById("viewDwtail");
var span = document.getElementsByClassName("close")[0];
btn.onclick = function() {
  modal.style.display = "block";
  document.body.classList.add("openModal"); // Add class to body
}
span.onclick = function() {
  modal.style.display = "none";
  document.body.classList.remove("openModal"); // Add class to body
}
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

// Date Range Selector
$(function() {
  $('input[name="daterange"]').daterangepicker({
    opens: 'left'
  }, function(start, end, label) {
    console.log("A new date selection was made: " + start.format('YYYY-MM-DD') + ' to ' + end.format('YYYY-MM-DD'));
  });
});


$(document).ready(function() {
  $('.select2-field').select2();

  // Data Table Initialization
  $('.infoTable').DataTable( {
    responsive: true,
    "searching": false,
    "lengthChange": false, 
    order: [[0, 'desc']] 
  });
});

new DataTable('#pdfInfoTable', {
  responsive: true,
  "searching": false,
  "lengthChange": false, 
});


//  Tables Action Button
$(document).ready(function() {
  var table = $('#pdfInfoTable').DataTable();

  $('#csvBtn').on('click', function() {
      // Download CSV
      var csv = table.buttons.exportData().toArray().join('\n');
      var blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      var link = document.createElement('a');
      var url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', 'data.csv');
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
  });

  $('#refreshBtn').on('click', function() {
      // Refresh table
      table.ajax.reload();
  });
});


// // Filters Dropdown
// function dropFilters() {
//   document.getElementById("filtersDropdown").classList.toggle("show");
// }

// window.onclick = function(event) {
//   if (!event.target.matches('.filterBtn')) {
//     var dropdowns = document.getElementsByClassName("filters-content");
//     var i;
//     for (i = 0; i < dropdowns.length; i++) {
//       var openDropdown = dropdowns[i];
//       if (openDropdown.classList.contains('show')) {
//         openDropdown.classList.remove('show');
//       }
//     }
//   }
// }
function toggleDropdown(id) {
  var element = document.getElementById(id);
  if (element.style.display === "block") {
    element.style.display = "none";
  } else {
    element.style.display = "block";
  }
}

function handleClick(text) {
  alert("Button clicked: " + text);
  document.getElementById("addFiltersDropdown").style.display = "none";
}
document.addEventListener("DOMContentLoaded", function () {
  var clickableDivs = document.querySelectorAll(
    ".row-bg.clickable"
  );

  clickableDivs.forEach(function (div) {
    div.addEventListener("click", function () {
      div.classList.toggle("active");
    });
  });
});

