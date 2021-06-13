document.getElementById("edit-profile-btn").onclick = () => {
    document.getElementById("profile-edit-menu").style.display = "flex";
}

document.getElementById("use-photo").onchange = () => {
    if(document.getElementById("use-photo").checked){
        document.getElementById("use-photo-label").style.color = "#0d0";
        document.getElementById("profile-image-label").style.display = "block";
    } else {
        document.getElementById("use-photo-label").style.color = "#fff";
        document.getElementById("profile-image-label").style.display = "none";
    }
}

document.getElementById("profile-image").onchange = (e) => {
    if(e.target.files[0]) {
        document.getElementById("profile-new-picture-preview").src = URL.createObjectURL(e.target.files[0])
        document.getElementById("profile-image-preview").style.display = "flex";
    } else {
        document.getElementById("profile-image-preview").style.display = "none";
    }
}

document.getElementById("use-preview-image").onclick = () => {
    document.getElementById("profile-image-preview").style.display = "none";
    document.getElementById("profile-image-label").style.fontWeight = 600;
    document.getElementById("profile-image-label").style.color = "#0f0";
    document.getElementById("profile-image-label").style.borderColor = "#0f0";
    document.getElementById("profile-image-label").style.borderWidth = "3px";
}

document.getElementById("cancel-preview-image").onclick = () => {
    document.getElementById("profile-image").value = "";
    document.getElementById("profile-image-preview").style.display = "none";
    document.getElementById("profile-image-label").style.fontWeight = 400;
    document.getElementById("profile-image-label").style.color = "#fff";
    document.getElementById("profile-image-label").style.borderColor = "#fff";
    document.getElementById("profile-image-label").style.borderWidth = "1px";
}


document.getElementById("edit-menu-form").onsubmit = () => {
    if(document.getElementById("Name").value.length < MIN_PROFILE_NAME || document.getElementById("Name").value.length > MAX_PROFILE_NAME){
        document.getElementById("name-warning").style.display = "flex";
        return false
    }

    if(document.getElementById("desc-profile").value.length > MAX_DESCRIPTION){
        document.getElementById("desc-warning").style.display = "flex";
        return false;
    }

    if(document.getElementById("USERName").value.length < MIN_PROFILE_USERNAME || document.getElementById("USERName").value.length > MAX_PROFILE_USERNAME){
        document.getElementById("username-warning").style.display = "flex";
        return false;
    }

    if(document.getElementById("use-photo").checked === true && document.getElementById("profile-image").value === "" || document.querySelector("#profile-image").value === null){
        document.getElementById("selected-but-not-selected").style.display = "flex";
        return false;
    }

    document.getElementById("post-form-new-form").childNodes[13].style.pointerEvents = "none";

    return true;
}


document.getElementById("new-post-btn").onclick = () => {
    document.getElementById("new-post-form").style.display = "flex";
}

document.getElementById("wanna-attach-files").onchange = () => {
    if(document.getElementById("wanna-attach-files").checked){
        document.getElementById("file-to-post-label").style.display = "block";
        document.getElementById("wanna-attach-files-label").style.color = "#0d0";
    } else {
        document.getElementById("file-to-post-label").style.display = "none";
        document.getElementById("wanna-attach-files-label").style.color = "#fff";
    }
}

document.getElementById("file-to-post").onchange = (e) => {
    if(e.target.files[0]){
        document.getElementById("post-details").style.fontSize = "18px";
        document.getElementById("file-to-post-label").style.borderColor = "#0f0";
        document.getElementById("file-to-post-label").style.color = "#0f0";
        document.getElementById("post-details").style.display = 'flex';
        document.getElementById("post-details").innerHTML = `
        <div>
            <h2>Selected File</h2>
            <div id="selected" style="word-break:break-all;">File : ${e.target.files[0].name}</div>
            <br/>
            MimeType : ${e.target.files[0].type}

            <button type="button" style="margin-top:20px" class="btns-usual" onclick="document.getElementById('post-details').style.display = 'none'">Ok</button>
        </div>
        `;
    } else {
        document.getElementById("post-details").innerHTML = null;
        document.getElementById("file-to-post-label").style.borderColor = "#fff";
        document.getElementById("file-to-post-label").style.color = "#fff";
    }

}


document.getElementById("post-form-new-form").onsubmit = () => {
    if((!document.getElementById("text-post").value || document.getElementById("text-post").value.trim() === "") && !document.getElementById("wanna-attach-files").checked ){
        document.getElementById("you-need-to-select-in-post").style.display = "flex";
        return false;
    }
    if(document.getElementById("wanna-attach-files").checked && !document.getElementById("file-to-post").value){
        document.getElementById("file-selected-but-not-selected").style.display  = "flex";
        return false;
    }
    return true;
}


document.getElementById("file-to-post-label").onclick = () => {
    if(document.getElementById("file-to-post").value){
        document.getElementById("file-to-post").value = null;
        document.getElementById("file-to-post-label").style.color = "#fff";
        document.getElementById("file-to-post-label").style.borderColor = "#fff";
        return false;
    }
}


document.getElementById('text-post').addEventListener('keydown', function(e) {
    if (e.key == 'Tab') {
        e.preventDefault();
        var start = this.selectionStart;
        var end = this.selectionEnd;

        // set textarea value to: text before caret + tab + text after caret
        this.value = this.value.substring(0, start) +
        "\t" + this.value.substring(end);

        // put caret at right position again
        this.selectionStart =
        this.selectionEnd = start + 1;
        return false;
    }
})

document.getElementById('desc-profile').addEventListener('keydown', function(e) {
    if (e.key == 'Tab') {
        e.preventDefault();
        var start = this.selectionStart;
        var end = this.selectionEnd;

        // set textarea value to: text before caret + tab + text after caret
        this.value = this.value.substring(0, start) +
        "\t" + this.value.substring(end);

        // put caret at right position again
        this.selectionStart =
        this.selectionEnd = start + 1;
        return false;
    }
});


document.getElementById("text-post").ondblclick = () => {
    document.getElementById("text-post").select();
    document.execCommand('copy');
}