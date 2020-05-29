    // https://stackoverflow.com/questions/1879872/django-update-div-with-ajax
    var url = "{% url 'status_update' %}";

    function updateChat() {
        $.getJSON(url, function(data){
            // Enumerate JSON
            document.getElementById("progress").innerHTML = data.progress;
            document.getElementById("s").innerHTML = data.s;
            if (data.progress < 100){
                setTimeout('updateChat()', 5000)
            } else {
                alert('Finished!')
            }

            });
        }
    updateChat()
