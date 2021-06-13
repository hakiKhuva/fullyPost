if(document.getElementById("profile-photo")){
    document.getElementById("profile-photo").onclick = () => {
        document.getElementById("img-full-screen").style.display = "flex";
    }
}

let interForJS = setInterval(() => {
    if(document.readyState === 'complete'){
        document.getElementById("loading-line").style.minWidth = "100%"
        setTimeout(()=>{
            document.getElementById("loading-line").style.display = "none";
        },150)
        clearInterval(interForJS)
    }
},400)

window.addEventListener("online",()=>{
    document.getElementById("offline-inf").style.display= "none";
    document.getElementById("online-inf").style.display = "block";
    setTimeout(() => {
        document.getElementById("online-inf").style.display = "none";
    }, 2500);
})
window.addEventListener("offline",()=>{
    document.getElementById("offline-inf").style.display= "block";
})

if(!navigator.onLine){
    document.getElementById("offline-inf").style.display= "block";
}



document.addEventListener("DOMContentLoaded", function() {
    var lazyloadImages = document.querySelectorAll(".lazy");
    var lazyloadThrottleTimeout;
    
    function lazyload () {
      if(lazyloadThrottleTimeout) {
        clearTimeout(lazyloadThrottleTimeout);
      }    
      
      lazyloadThrottleTimeout = setTimeout(function() {
          var scrollTop = window.pageYOffset;
          lazyloadImages.forEach(function(img) {
              if(img.offsetTop < (window.innerHeight + scrollTop)) {
                img.src = img.dataset.src;
                img.classList.remove('lazy');
              }
          });
          if(lazyloadImages.length == 0) { 
            document.removeEventListener("scroll", lazyload);
            window.removeEventListener("resize", lazyload);
            window.removeEventListener("orientationChange", lazyload);
          }
      }, 20);
    }
    
    document.addEventListener("scroll", lazyload);
    window.addEventListener("resize", lazyload);
    window.addEventListener("orientationChange", lazyload);
  });