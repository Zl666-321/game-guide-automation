document.addEventListener('DOMContentLoaded',()=>{
    const cards=document.querySelectorAll('.card');
    const o=new IntersectionObserver(entries=>{
        entries.forEach(e=>{if(e.isIntersecting){e.target.style.opacity='1';e.target.style.transform='translateY(0)'}})
    },{threshold:.1});
    cards.forEach(c=>{c.style.opacity='0';c.style.transform='translateY(20px)';c.style.transition='all .5s ease';o.observe(c)})
});