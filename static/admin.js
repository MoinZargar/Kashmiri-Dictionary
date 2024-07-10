$(document).ready( function () {
    $('#test-report').DataTable();
  } );
  
  
  let menuicn = document.querySelector(".menuicn");
  let nav = document.querySelector(".navcontainer");
  
  menuicn.addEventListener("click",()=>
  {
      nav.classList.toggle("navclose");
  })

  

  function updateTableContent(data) {
   console.log(data);
   var tableBody = $('#tableContent');
   tableBody.empty(); // Clear existing table rows
   
   for (var i = 0; i < data.length; i++) {
     var item = data[i];
     var newRow = '<tr class="data">' +
       '<td class="data cell">' + item[1] + '</td>' +
       '<td class="data cell">' + item[2] + '</td>' +
       '<td class="data cell">' + item[3] + '</td>' +
       '<td class="data cell">' + item[5] + '</td>' +
       '<td class="data cell">' + item[4] + '</td>' +
       '<td class="data cell">' + item[6] + '</td>' +
       '<td class="data"><button type="button" onclick="approve(\'' + item[0] + '\')" class="btn btn-sm btn-success">Add</button></td>' +
       '<td class="data"><button type="button" onclick="reject(\'' + item[0] + '\')" class="btn btn-sm btn-danger">Delete</button></td>' +
       '</tr>';
       
     tableBody.append(newRow);
   }
 }
 
 // AJAX request to fetch updated data
 function reject(id){
   $.ajax({
      type: "POST",
      url: "/admin_action",
      data: { 
         id:id,
         action:"delete"
      },
      success: function(response) {
         updateTableContent(response); // Update table content with the fetched data
       }
      
   });
 }

 function approve(id){
   $.ajax({
       type: "POST",
       url: "/admin_action",
       data: { 
          id:id,
          action:"add"
       },
       success: function(response) {
         updateTableContent(response); // Update table content with the fetched data
       }
    });
 }
 