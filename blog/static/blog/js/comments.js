document.addEventListener("DOMContentLoaded", () => {

document.querySelectorAll(".reply-toggle").forEach(btn=>{

btn.addEventListener("click", ()=>{

const id = btn.dataset.id

const form =
document.getElementById(`reply-form-comment-${id}`) ||
document.getElementById(`reply-form-reply-${id}`)

if(!form) return

form.style.display =
form.style.display === "none"
? "block"
: "none"

})

})

})