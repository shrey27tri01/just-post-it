document.addEventListener('DOMContentLoaded', () => {

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
   }

     var editButtons = document.querySelectorAll('.edit-button');
     var tweetContents = document.querySelectorAll('.tweet-content');
    // console.log(editButtons);
    // console.log(tweetContents);

    if (editButtons) {
      editButtons.forEach(editButton => {
        editButton.onclick = () => {
          var contentToBeEdited = editButton.parentElement.children[0].innerHTML;
          var editContent = editButton.parentElement;
          var newItem = document.createElement('span');
          newItem.innerHTML = `<textarea class='new-content'>${contentToBeEdited}</textarea>`;
          editContent.replaceChild(newItem, editContent.children[0]);
          editContent.children[1].innerHTML = "Save";
          var saveButton = editContent.children[1];
          saveButton.onclick = () => {
            var tweetId = saveButton.parentElement.parentElement.children[0].innerHTML;
            // console.log(tweetId);
            var newContent = document.querySelector('.new-content').value;
            // console.log(`Your new content is: ${newContent}`);
            // console.log(newContent.length);
            if (newContent.length === 0) {
              alert("You can't post nothing!");
              return;
            }
            let jsonNewContent = JSON.stringify({'content': newContent});

            const request = new XMLHttpRequest();
            const csrftoken = getCookie('csrftoken');
            request.open('POST', `/edit/${tweetId}`);
            request.setRequestHeader("Content-Type", "application/json");
            if (csrftoken){
              request.setRequestHeader("HTTP_X_REQUESTED_WITH", "XMLHttpRequest")
              request.setRequestHeader("X-Requested-With", "XMLHttpRequest")
              request.setRequestHeader("X-CSRFToken", csrftoken)
            }
            request.onload = () => {
              // const response = request.responseText;
              // console.log(request.status);
              if (request.status === 200) {
                newItem.innerHTML = `${newContent}`;
                editContent.children[1].innerHTML = "Edit";
                // console.log(editButton);
              } else {
                alert("An error occurred. Please try again.");
                return;
              }
            };
            request.send(jsonNewContent);
          
            // saveButton = editButton;
            // console.log(editButton, saveButton);
          };
        };
        // console.log(editButton);
      });
    }

});
