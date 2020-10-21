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

    var button = document.querySelector('.post-button');
    var username = document.querySelector('.username').innerHTML;
    var followerCount = document.querySelector('.followerCount').innerHTML;
    // console.log(username);
    button.onclick = event => {
        event.preventDefault();
        // console.log(button);
        const request = new XMLHttpRequest();
        const csrftoken = getCookie('csrftoken');
        request.open('POST', `/user/${username}`);
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
                const count = JSON.parse(request.response)["followerCount"];
                // console.log(action);
                // console.log(followerCount);
                if (action === "followed") {
                    button.className = "but post-button btn btn-danger";
                    button.innerHTML = "Unfollow";
                    document.querySelector('.followerCount').innerHTML = count;
                } else if (action === "unfollowed") {
                    button.className = "but post-button btn btn-success";
                    button.innerHTML = "Follow";
                    document.querySelector('.followerCount').innerHTML = count;
                }
            } else {
                alert("An error occurred. Please try again.");
                return;
            }
        };
        request.send();
    };
});