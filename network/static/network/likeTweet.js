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
    };

    var buttons = document.querySelectorAll(".button");
    buttons.forEach(button => {
        var tweetId = button.parentElement.parentElement.children[1].innerHTML;
        button.onclick = () => {
            // const jsonAction = JSON.stringify({"action": action});
            const request = new XMLHttpRequest();
            const csrftoken = getCookie('csrftoken');
            request.open('POST', `/like/${tweetId}`);
            request.setRequestHeader("Content-Type", "application/json");
            if (csrftoken){
                request.setRequestHeader("HTTP_X_REQUESTED_WITH", "XMLHttpRequest")
                request.setRequestHeader("X-Requested-With", "XMLHttpRequest")
                request.setRequestHeader("X-CSRFToken", csrftoken)
            };
            request.onload = () => {
                // console.log(request);
                if (request.status === 200) {
                    const action = JSON.parse(request.response)["action"];
                    const count = JSON.parse(request.response)["likeCount"];
                    button.parentElement.parentElement.children[5].innerHTML = count;
                    // console.log(action);
                    if (action === "liked") {
                        button.innerHTML = "Unlike";
                    } else if (action === "unliked") {
                        button.innerHTML = "Like";
                    }
                } else {
                    alert("An error occurred. Please try again.");
                    return;
                }
            };
            request.send();   
        };
    });
});