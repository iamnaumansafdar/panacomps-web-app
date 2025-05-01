document.addEventListener("DOMContentLoaded", function() {
    var textarea = document.getElementById("id_details");
    if (textarea) {
        console.log('Textarea found');
        textarea.addEventListener("input", function() {
            var charCount = document.getElementById("charCount");
            if (charCount) {
                charCount.textContent = textarea.value.length + " characters";
            }
        });
    } else {
        console.log('Textarea not found');
    }
});



// Get the modal
var modal = document.getElementById("viewDwtailModal");
var btn = document.getElementById("viewHistory");
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

// View history model

var historyModal = document.getElementById("viewHistoryModal");
var historyBtn = document.getElementById("viewHistory");
var closeHistory = historyModal.getElementsByClassName("close")[0];
historyBtn.onclick = function() {
  historyModal.style.display = "block";
  document.body.classList.add("openModal");
}
closeHistory.onclick = function() {
  historyModal.style.display = "none";
  document.body.classList.remove("openModal");
}
window.onclick = function(event) {
  if (event.target == historyModal) {
    historyModal.style.display = "none";
    document.body.classList.remove("openModal");
  }
}


$(document).ready(function() {
  $('.select2-field').select2();
});

// Filter on the view detail button
function dropFilters() {
  document.getElementById("filterDropdown").classList.toggle("show");
}

window.onclick = function(event) {
  if (!event.target.matches('.filtersBtn')) {
    var dropdowns = document.getElementsByClassName("filter-contents");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}
function toggleDropdowns(id) {
  var element = document.getElementById(id);
  if (element.style.display === "block") {
    element.style.display = "none";
  } else {
    element.style.display = "block";
  }
}

function handleClick(text) {
  alert("Button clicked: " + text);
  document.getElementById("addFilterDropdowns").style.display = "none";
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

