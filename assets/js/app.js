
let STATE = { lang: 'de', content: null };

async function loadContent() {
  const res = await fetch('content.json');
  STATE.content = await res.json();
  renderAll();
}

// Helpers
function qs(sel){ return document.querySelector(sel); }
function qsa(sel){ return document.querySelectorAll(sel); }

function setLang(lang){
  STATE.lang = lang;
  document.documentElement.lang = lang;
  document.documentElement.dir = (lang==='fa') ? 'rtl' : 'ltr';
  renderAll();
}

// Render functions
function renderNav(){
  const { content } = STATE;
  const t = content[STATE.lang];
  qs('#brand').textContent = t.brand;
  const nav = t.nav;
  const map = ['#nav-services','#nav-courses','#nav-about','#nav-gallery','#nav-reviews','#nav-contact'];
  nav.forEach((label, i)=>{ qs(map[i]).textContent = label; });
  qsa('.btn-book-now').forEach(el=>el.textContent = t.labels.book_now || t.cta_book || 'Book');
}

function renderHero(){
  const { content } = STATE;
  const t = content[STATE.lang];
  qs('#hero-title').innerHTML = t.hero_title;
  qs('#hero-sub').textContent = t.hero_sub;
  qs('#hero-img').setAttribute('src', content.media.hero);
}

function renderServices(){
  const t = STATE.content[STATE.lang].sections;
  qs('#services-title').textContent = t.services_title;
  qs('#services-img').setAttribute('src', STATE.content.media.services);
  const ul = qs('#services-list'); ul.innerHTML='';
  t.services_points.forEach(p=>{
    const li = document.createElement('li');
    li.textContent = p; ul.appendChild(li);
  });
}

function renderCourses(){
  const t = STATE.content[STATE.lang].sections;
  qs('#courses-title').textContent = t.courses_title;
  qs('#courses-text').textContent = t.courses_text;
  const ul = qs('#courses-bullets'); ul.innerHTML='';
  t.courses_bullets.forEach(p=>{ const li=document.createElement('li'); li.textContent=p; ul.appendChild(li); });
  qs('#courses-img').setAttribute('src', STATE.content.media.courses);
}

function renderAbout(){
  const t = STATE.content[STATE.lang].sections;
  qs('#about-title').textContent = t.about_title;
  qs('#about-text').textContent = t.about_text;
  qs('#about-img').setAttribute('src', STATE.content.media.about);
}

function renderGallery(){
  const t = STATE.content[STATE.lang].sections;
  qs('#gallery-title').textContent = t.gallery_title;
  const g = qs('#gallery-grid'); g.innerHTML='';
  STATE.content.media.gallery.forEach(src=>{
    const img = document.createElement('img');
    img.src = src; img.alt="Gallery";
    img.className="w-full h-56 object-cover rounded-xl shadow";
    g.appendChild(img);
  });
}

function renderTestimonials(){
  const t = STATE.content[STATE.lang].sections;
  qs('#reviews-title').textContent = t.testimonials_title;
  const wrap = qs('#reviews-wrap'); wrap.innerHTML='';
  t.testimonial_list.forEach((item, idx)=>{
    const card = document.createElement('div');
    card.className="bg-white p-6 rounded-xl shadow";
    card.innerHTML = `<div class="mb-2">★★★★★</div><p class="text-gray-700 italic mb-2">"${item.t}"</p><p class="text-sm font-semibold">${item.a}</p>`;
    wrap.appendChild(card);
  });
}

function renderContact(){
  const lang = STATE.lang;
  const t = STATE.content[lang].sections;
  const labels = STATE.content[lang].labels;
  qs('#contact-title').textContent = t.contact_title;
  qs('#contact-text').textContent  = t.contact_text;
  qs('#label-name').textContent    = labels.name;
  qs('#label-email').textContent   = labels.email;
  qs('#label-message').textContent = labels.message;
  qs('#btn-send').textContent      = labels.send;
  qs('#hours-label').textContent   = labels.hours;
  qs('#by-appt').textContent       = labels.by_appt;
}

function renderAll(){
  if(!STATE.content) return;
  renderNav();
  renderHero();
  renderServices();
  renderCourses();
  renderAbout();
  renderGallery();
  renderTestimonials();
  renderContact();
}

// Language switch handlers
document.addEventListener('click', (e)=>{
  if(e.target.matches('[data-lang]')){
    setLang(e.target.getAttribute('data-lang'));
  }
});

// Chatbot (scripted Q&A)
function addChat(msg, who='bot'){
  const wrap = qs('#chat-messages');
  const div = document.createElement('div');
  div.className = 'mb-2 ' + (who==='user' ? 'text-right':'text-left');
  const bubble = document.createElement('div');
  bubble.className = (who==='user' ? 'inline-block bg-amber-700 text-white':'inline-block bg-gray-100 text-gray-800') + ' px-3 py-2 rounded-2xl max-w-xs';
  bubble.textContent = msg;
  div.appendChild(bubble);
  wrap.appendChild(div);
  wrap.scrollTop = wrap.scrollHeight;
}

function bestAnswer(q){
  const lang = STATE.lang;
  const faq = STATE.content.faq;
  const low = q.toLowerCase();
  for(const item of faq){
    if(item.q.some(k => low.includes(k.lower ? k.lower : k.toLowerCase()))){
      return item.a[lang] || item.a['de'];
    }
  }
  return (lang==='fa') ? 'لطفاً سوال خود را دقیق‌تر بپرسید.' : (lang==='en' ? 'Please ask a more specific question.' : 'Bitte stellen Sie Ihre Frage genauer.');
}

qs('#chat-toggle').addEventListener('click', ()=>{
  qs('#chat-window').classList.toggle('hidden');
});

qs('#chat-send').addEventListener('click', ()=>{
  const inp = qs('#chat-input');
  const v = inp.value.trim();
  if(!v) return;
  addChat(v, 'user');
  inp.value='';
  setTimeout(()=> addChat(bestAnswer(v), 'bot'), 400);
});

qs('#chat-input').addEventListener('keypress', (e)=>{
  if(e.key==='Enter'){ qs('#chat-send').click(); }
});

loadContent();
