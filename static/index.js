

let resultsDiv = document.getElementById("results");
const form = document.getElementById("search-form");
const input = document.getElementById("search-input");
const suggestionsList = document.getElementById("suggestions");
//used for fetching data of searched word from db
function load_Data(word){
    $.ajax({
        type: "POST",
        url: "/result",
        data: { 
        word:word
        },
        success: function(response) {
          const wordData=response[0];
          if (wordData) {
            document.getElementById("card").style.visibility="visible";
            document.getElementById("english-word").innerHTML=wordData[1];
            document.getElementById("pos").innerHTML=wordData[2];
            document.getElementById("english-meaning").innerHTML=wordData[3];
            document.getElementById("kashmiri-meaning").innerHTML=wordData[4];
          } else {
            document.getElementById("card").style.visibility="visible";
            document.getElementById("english-word").innerHTML="Not Found";
            document.getElementById("pos").innerHTML=" ";
            document.getElementById("english-meaning").innerHTML=" ";
            document.getElementById("kashmiri-meaning").innerHTML=" ";
          }
          // Clear the suggestions list
          const suggestionsList = document.getElementById("suggestions");
          suggestionsList.innerHTML = "";
        }
    });
}
 
    input.addEventListener("input", event => {
      document.getElementById("card").style.visibility="hidden";
      const inputValue = event.target.value;
      if(inputValue!=''){
        $.ajax({
            type: "POST",
            url: "/suggestion",
            data: { 
            inputValue:inputValue
            },
            success: function(response) {
               
       
                const suggestions=response;
                suggestionsList.innerHTML = "";
                if (suggestions.length > 0) {
                    suggestions.forEach(suggestion => {
                    const suggestionEl = document.createElement("li");
                    suggestionEl.innerHTML = suggestion[1];
                    suggestionEl.addEventListener("click", () => {
                        // When a suggestion is clicked, fill the input field and search for the word
                        input.value = suggestion[1];
                        load_Data(input.value);
                        form.dispatchEvent(new Event("submit"));
                    });
                    suggestionsList.appendChild(suggestionEl);
                    });
                }
            }
                
                
        
   });
   }
               

});
    
 
    form.addEventListener("submit", async event => {
      event.preventDefault();
      const word = input.value;
      input.value = "";
      if(word!=''){
        load_Data(word);    
}
      
    });

