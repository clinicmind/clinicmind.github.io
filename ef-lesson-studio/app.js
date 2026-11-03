(function(){
  'use strict';
  const $=id=>document.getElementById(id);
  const {build,escapeHTML,normalizeText}=window.EFEngine;
  const state={result:null,activeTab:'notes',mode:'both',lastInput:null,sourceFile:''};
  const demo=`水循環與我們的生活
水循環是地球上的水在不同地方及狀態之間持續移動的過程。太陽提供能量，使海洋、河流和湖泊中的液態水受熱蒸發，成為空氣中的水蒸氣。植物亦會透過蒸散作用將水分釋放到空氣中。
水蒸氣上升後遇到較冷的空氣，可能凝結成細小的水滴。大量微小的水滴聚集後便形成雲。當雲中的水滴互相結合，逐漸變得較大，便可能以雨、雪或冰雹的形式降落到地面，這個過程稱為降水。
降落到地面的水，有一部分滲進土壤並成為地下水；另一部分則經溪流和河流返回海洋。水亦可被植物吸收，之後重新進入大氣。水循環沒有固定的起點和終點，各個過程會不斷重複。
水循環有助調節環境中的水分分布，影響天氣、植物生長和人類的用水。當一個地區長期缺少降水時，當地的可用水資源可能減少。因此，認識水循環有助我們了解水資源和環境之間的關係。`;
  const grades={p1:'小學一至三年級',p2:'小學四至六年級',s1:'中學初中',s2:'中學高中'};
  const notesView=$('notes-view'),worksheetView=$('worksheet-view'),keyView=$('key-view');
  function footer(type,page){return `<footer class="paper-footer"><span>EF 教學工作室 · ${type} · ${page}</span><span>Hill · Skill · Will｜教師自訂教材</span></footer>`;}
  function header(d,type,code,sub='',page=''){
    return `<header class="paper-head"><div><div class="paper-kicker">HILL · SKILL · WILL / ${escapeHTML(type)}</div><h2 data-editable="true">${escapeHTML(d.title)}</h2><div class="paper-subtitle" data-editable="true">${escapeHTML(sub)}</div></div><span class="paper-id">${code}</span></header><div class="paper-fields"><span>姓名：<span class="longline"></span></span><span>班別：<span class="longline"></span></span><span>日期：<span class="longline"></span></span></div>`;
  }
  function hill(d){return `<div class="note-banner"><span class="badge-letter">H</span><div><strong>HILL｜今日要到達哪裡？</strong><p data-editable="true">${escapeHTML(d.goal)}</p><p>我會用一句話解釋：完成後，我需要做到 <span class="blank">＿＿＿＿＿＿＿＿＿＿＿＿＿＿</span>。</p></div></div>`;}
  function skillSteps(){return `<div class="task-steps"><div><b>STEP 01｜準備</b><span data-editable="true">閱讀題目，圈重要字詞</span></div><div><b>STEP 02｜組織</b><span data-editable="true">分段完成筆記／表格</span></div><div><b>STEP 03｜核對</b><span data-editable="true">回到課文，找原文依據</span></div></div>`;}
  function notesHTML(d){
    const noteRows=d.cloze.map((x,i)=>`<li><span class="num">${String(i+1).padStart(2,'0')}</span><span data-editable="true">${x.html}</span></li>`).join('');
    const bank=d.banks.length?`<div class="word-bank"><strong>提示詞庫</strong>${d.banks.map(w=>`<span class="word-chip" data-editable="true">${escapeHTML(w)}</span>`).join('')}</div>`:'<p class="small-tip">本版不顯示詞庫。如學生需要額外提示，教師可改用較多支持版本。</p>';
    return `<article class="paper">${header(d,'HALF-FILLED NOTES','N–01','半完成筆記｜從原文提取重點、外化工作記憶')}${hill(d)}<section class="paper-section"><h3><span class="section-n">01 / SKILL</span> 閱讀與關鍵詞提取</h3><p class="instruction">請先閱讀課文，再根據上下文填寫空格。遇到困難時，可先圈出原文中有關的字詞。</p>${bank}<ol class="note-list">${noteRows}</ol></section>${footer('半完成筆記',1)}</article>
      <article class="paper">${header(d,'HALF-FILLED NOTES','N–02','半完成筆記｜組織、核對與反思')}
        <section class="paper-section"><h3><span class="section-n">02 / SKILL</span> 把重點組織起來</h3><p class="instruction">選三個你認為最重要的概念；寫出它們的關係。若課文沒有明確說明，請標示「待查」。</p><table class="organizer"><thead><tr><th>關鍵概念</th><th>課文中的解釋／證據</th><th>我會怎樣記住？</th></tr></thead><tbody><tr><td data-editable="true">${escapeHTML(d.keywords[0]||'＿＿＿＿')}</td><td></td><td></td></tr><tr><td data-editable="true">${escapeHTML(d.keywords[1]||'＿＿＿＿')}</td><td></td><td></td></tr><tr><td data-editable="true">${escapeHTML(d.keywords[2]||'＿＿＿＿')}</td><td></td><td></td></tr></tbody></table></section>
        <section class="paper-section"><h3><span class="section-n">03 / SKILL</span> 我的三步工作流程</h3>${skillSteps()}</section>
        <section class="paper-section"><h3><span class="section-n">04 / WILL</span> 困難時，我可以先開始</h3><p class="instruction">如果我卡住，先做一個 90 秒內可以完成的小動作：</p><div class="choice-line"><span><span class="choice-box"></span>再讀一句</span><span><span class="choice-box"></span>圈一個關鍵詞</span><span><span class="choice-box"></span>向同桌解釋第一步</span></div><p class="instruction">我下一次會保留的策略：</p><div class="paper-lines short"></div></section>${footer('半完成筆記',2)}</article>`;
  }
  function worksheetHTML(d){
    const choice=d.choices.map(x=>`<span><span class="choice-box"></span>${escapeHTML(x)}</span>`).join('');
    return `<article class="paper">${header(d,'EF WORKSHEET','W–01','任務規劃｜目標、方法、證據')}
      <section class="hsw-block hill"><div class="hsw-title">HILL <small>— 目標、意義和成功準則</small></div><p>我知道今天要完成甚麼嗎？</p><div class="note-banner" style="margin:9px 0 12px"><span class="badge-letter">H</span><div><strong>本課目標</strong><p data-editable="true">${escapeHTML(d.goal)}</p></div></div><p class="hsw-prompt" data-editable="true">① 我最想透過這篇課文弄明白的問題是：</p><div class="paper-lines tiny"></div><p class="hsw-prompt">② 我怎樣知道自己已經學會？請寫一個可觀察的標準。</p><div class="paper-lines tiny"></div></section>
      <section class="hsw-block skill"><div class="hsw-title">SKILL <small>— 計劃、組織和自我監控</small></div><p>開始之前，先把「我應該怎樣做」寫出來。</p>${skillSteps()}<p class="hsw-prompt">我估計最需要協助的是哪一步？</p><div class="choice-line"><span><span class="choice-box"></span>開始任務</span><span><span class="choice-box"></span>找重點</span><span><span class="choice-box"></span>組織資料</span><span><span class="choice-box"></span>檢查答案</span></div><p class="hsw-prompt">從課文找出兩項關鍵資訊，並標示原文句子：</p><table class="organizer"><thead><tr><th>我找到的資訊</th><th>出處／原文根據</th></tr></thead><tbody><tr><td></td><td></td></tr><tr><td></td><td></td></tr></tbody></table></section>${footer('執行功能工作紙',1)}</article>
      <article class="paper">${header(d,'EF WORKSHEET','W–02','閱讀思考｜自主選擇、持續投入與反思')}
      <section class="hsw-block skill"><div class="hsw-title">SKILL <small>— 轉化知識，而不只抄寫</small></div><p>根據課文作答；沒有充分根據時，可寫「課文未提供」。</p><ol class="question-list">${d.questions.map(q=>`<li data-editable="true">${escapeHTML(q)}</li>`).join('')}</ol><p class="hsw-prompt">如果我原本的方法不成功，可以改用甚麼方法？</p><div class="paper-lines tiny"></div></section>
      <section class="hsw-block will"><div class="hsw-title">WILL <small>— 自主性、投入與面對阻力</small></div><p>請選一種方式呈現你學到的內容（內容標準相同，表達方式可以選）。</p><div class="choice-line">${choice}</div><p class="hsw-prompt">我可能會遇到的阻力：<span class="blank">＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿</span></p><p class="hsw-prompt">當阻力出現，我可以先做的 90 秒小步驟：</p><div class="paper-lines tiny"></div><p class="hsw-prompt">完成後，我想對自己說的一句具體回饋：</p><div class="paper-lines tiny"></div></section>
      <section class="paper-section"><h3><span class="section-n">EXIT TICKET</span> 我的策略回顧</h3><div class="choice-line"><span><span class="choice-box"></span>我能說出本課目標</span><span><span class="choice-box"></span>我有用到一項策略</span><span><span class="choice-box"></span>我有回到原文核對</span></div><p class="instruction">下一次我會：<span class="blank">＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿</span></p></section>${footer('執行功能工作紙',2)}</article>`;
  }
  function answerHTML(d){
    let rows=d.cloze.map((x,i)=>`<tr><td>${i+1}</td><td>${x.answer?escapeHTML(x.answer):'需教師補充'}</td><td>${escapeHTML(x.source)}</td></tr>`).join('');
    const checks=['檢查填空是否為真正的學科關鍵字，而非通用詞語。','逐題核對課文原句，確認沒有割裂語境或改變原意。','確認 Hill 目標符合實際課堂的可觀察成果。','從學生表現辨識要教的策略，而不是診斷或評價人格。','依學生掌握情況，逐步撤除詞庫、首步提示或檢查卡。'];
    return `<article class="paper">${header(d,'TEACHER KEY','T–01','教師參考答案｜不宜隨學生工作紙一同派發')}
      <div class="key-note"><strong>此頁為教師核對用。</strong>填空答案由課文片段原字抽取。開放式問題不設唯一標準答案，須教師依原文及課程標準判斷。產生器不會核實課文自身的科學或歷史正確性。</div>
      <section class="paper-section"><h3><span class="section-n">答案</span> 半完成筆記填空對照</h3><table class="answer-table"><thead><tr><th>#</th><th>填空詞</th><th>原文依據</th></tr></thead><tbody>${rows}</tbody></table></section>
      <section class="paper-section"><h3><span class="section-n">教學</span> 一位老師、35 人的大班流程</h3><div class="task-steps"><div><b>1–2 分鐘 / Hill</b><span>顯示可觀察的成功標準</span></div><div><b>2–5 分鐘 / Skill</b><span>示範第一題、示範核對</span></div><div><b>2 分鐘 / Will</b><span>由學生選小步驟與反思</span></div></div><p class="instruction">可使用全班統一流程、同桌互核；對部分學生額外提供詞庫或段落提示，無須逐人製作不同材料。</p></section>
      <section class="paper-section"><h3><span class="section-n">審核</span> 發給學生前的五項檢查</h3><ol class="question-list">${checks.map(x=>`<li>${escapeHTML(x)}</li>`).join('')}</ol></section>
      <div class="key-note"><strong>參考：</strong>Moran & Gardner (2018), Ch. 2；Meltzer (2018), Ch. 11；依學科可參照 Chs. 8–10、12–14。本文模板是原創教學化設計，不是原書量表或出版社授權教材。</div>${footer('教師答案',1)}</article>`;
  }
  function setEditable(yes){
    document.body.classList.toggle('contenteditable-enabled',yes);
    document.querySelectorAll('#preview-output [data-editable]').forEach(el=>{
      el.contentEditable=yes?'true':'false';el.spellcheck=false;
      if(yes)el.setAttribute('title','點擊文字可編輯');else el.removeAttribute('title');
    });
  }
  function showTab(tab){
    state.activeTab=tab;
    for(const [name,pane] of [['notes',notesView],['worksheet',worksheetView],['key',keyView]])pane.hidden=tab!==name;
    document.querySelectorAll('.tab').forEach(x=>{const active=x.dataset.tab===tab;x.classList.toggle('active',active);x.setAttribute('aria-selected',String(active));});
  }
  function render(d){
    notesView.innerHTML=notesHTML(d);worksheetView.innerHTML=worksheetHTML(d);keyView.innerHTML=answerHTML(d);
    $('preview-output').hidden=false;$('empty-state').hidden=true;$('output-actions').hidden=false;
    $('generation-status').innerHTML='<span class="status-dot"></span> 已產出 · 本機處理';
    $('output-caution').lastElementChild.textContent=d.flags.length?d.flags.join(' ')+'；此外，請核對所有關鍵詞與原文。':'這是依文字規則製作的原創教學範本，不是生成式 AI 語意分析。請核對填空、學科目標、答案及原文。';
    setEditable($('edit-toggle').checked);
    showTab(d.mode==='worksheet'?'worksheet':'notes');
  }
  function readInput(){return {worksheetTitle:$('lesson-title').value,subject:$('subject').value,grade:$('grade').value,scaffold:$('scaffold').value,mode:$('output-mode').value,goal:$('goal').value,keywords:$('teacher-keywords').value,text:$('lesson-text').value};}
  function generate(){
    try{
      const input=readInput(),r=build(input);state.lastInput=input;state.result=r;state.mode=input.mode;
      $('form-message').textContent='';render(r);
      if(window.innerWidth<860)$('preview-stage').scrollIntoView({behavior:'smooth',block:'start'});
    }catch(err){$('form-message').textContent=err.message||'無法產生教材，請檢查課文內容。';}
  }
  function loadDemo(){
    $('lesson-title').value='水循環與我們的生活';$('subject').value='science';$('grade').value='p2';
    $('goal').value='能說明蒸發、凝結、降水的關係，並用課文證據完成水循環流程圖。';
    $('teacher-keywords').value='蒸發、凝結、降水、水循環、蒸散作用';$('lesson-text').value=demo;
    $('char-count').textContent=normalizeText(demo).length.toLocaleString('zh-Hant')+' 字';generate();
  }
  function safeName(s){return String(s||'EF工作紙').replace(/[\\/:*?"<>|]/g,'_').slice(0,35);}
  function exportSubset(){
    const mode=state.activeTab==='key'?'key':state.mode;
    return mode==='notes'?notesView.innerHTML:mode==='worksheet'?worksheetView.innerHTML:mode==='key'?keyView.innerHTML:notesView.innerHTML+worksheetView.innerHTML;
  }
  function getCss(){
    try{const sheet=[...document.styleSheets].find(x=>x.href?.includes('styles.css'));if(sheet)return Array.from(sheet.cssRules).map(x=>x.cssText).join('\n');}catch(_e){}
    return 'body{font-family:"Microsoft JhengHei",sans-serif}.paper{page-break-after:always;padding:20px}.paper h2{font-size:22pt}.note-banner,.hsw-block{padding:15px;border:1px solid #aaa;margin:12px 0}.organizer,.answer-table{border-collapse:collapse;width:100%}.organizer td,.organizer th,.answer-table td,.answer-table th{border:1px solid #aaa;padding:9px}';
  }
  function documentHTML(){
    const content=exportSubset();
    const title=escapeHTML(state.result?.title||'EF 教材');
    const css=getCss()+"\nhtml,body{background:#fff!important;} .paper{box-shadow:none!important;max-width:190mm;min-height:0;margin:auto auto 12mm;break-after:page;} .no-print{display:none!important;}";
    return '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><title>'+title+' · Hill Skill Will</title><style>'+css+'</style></head><body><main>'+content+'</main></body></html>';
  }
  function downloadBlob(blob,filename){const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);}
  function setPrintClass(mode){document.body.classList.remove('print-notes','print-worksheet','print-key','print-both');document.body.classList.add('print-'+mode);}
  function printNow(){if(!state.result)return;setPrintClass(state.activeTab==='key'?'key':state.mode);window.print();}
  async function parseDocx(file){
    if(!window.JSZip)throw Error('未能載入 DOCX 解壓縮程式，請改用 TXT 或直接貼上課文。');
    const zip=await window.JSZip.loadAsync(await file.arrayBuffer());const entry=zip.file('word/document.xml');
    if(!entry)throw Error('找不到 Word 文件內容，請另存為 .docx 後重試。');
    const xml=await entry.async('string');const doc=new DOMParser().parseFromString(xml,'application/xml');
    const ns='http://schemas.openxmlformats.org/wordprocessingml/2006/main';
    const p=[...doc.getElementsByTagNameNS(ns,'p')].map(para=>[...para.getElementsByTagNameNS(ns,'t')].map(x=>x.textContent).join('')).filter(Boolean);
    return p.join('\n');
  }
  async function loadPdfJS(){
    if(window.pdfjsLib)return window.pdfjsLib;
    await new Promise((resolve,reject)=>{
      const el=document.createElement('script');el.src='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
      el.onload=resolve;el.onerror=()=>reject(new Error('無法下載 PDF 文字解析器。請將 PDF 文字複製貼上，或改用 TXT / DOCX。'));
      document.head.appendChild(el);
      setTimeout(()=>{if(!window.pdfjsLib)reject(new Error('PDF 解析器未能載入。請貼上課文文字。'));},13000);
    });
    window.pdfjsLib.GlobalWorkerOptions.workerSrc='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
    return window.pdfjsLib;
  }
  async function parsePDF(file){
    const pdfjs=await loadPdfJS();const doc=await pdfjs.getDocument({data:new Uint8Array(await file.arrayBuffer())}).promise;
    const chunks=[];for(let i=1;i<=doc.numPages;i++){
      const page=await doc.getPage(i);const content=await page.getTextContent();
      const lines=[];let priorY=null;let acc='';
      for(const item of content.items){if(!item.str)continue;const y=item.transform?.[5]||0;
        if(priorY!==null&&Math.abs(y-priorY)>4&&acc.trim()){lines.push(acc.trim());acc='';}
        acc+=(/[\u3400-\u9fff]/.test(item.str)?'':' ')+item.str;priorY=y;
      }
      if(acc.trim())lines.push(acc.trim());chunks.push(lines.join('\n'));
    }
    let txt=chunks.join('\n\n');if(txt.replace(/\s/g,'').length<50)throw Error('這份 PDF 可能是掃描圖片，暫未支援 OCR。請上載有文字層的 PDF，或複製課文文字。');
    return txt;
  }
  async function loadFile(file){
    if(!file)return;if(file.size>14*1024*1024)throw Error('單一檔案上限為 14 MB；請分段處理。');
    const name=file.name.toLowerCase();let text;
    if(/\.docx$/.test(name))text=await parseDocx(file);
    else if(/\.pdf$/.test(name))text=await parsePDF(file);
    else if(/\.(txt|md|html|htm)$/.test(name))text=await file.text();
    else throw Error('請上載 TXT、MD、DOCX、PDF 或 HTML。');
    text=normalizeText(text);if(text.length<75)throw Error('檔案無法抽取足夠的可閱讀文字，請直接貼上課文。');
    $('lesson-text').value=text;$('char-count').textContent=text.length.toLocaleString('zh-Hant')+' 字';
    if(!$('lesson-title').value.trim())$('lesson-title').value=file.name.replace(/\.[^.]+$/,'').slice(0,70);
    state.sourceFile=file.name;$('file-status').classList.remove('error');$('file-status').textContent='已讀取 '+file.name+'（只在瀏覽器處理）';
  }
  $('lesson-form').addEventListener('submit',event=>{event.preventDefault();generate();});
  $('lesson-text').addEventListener('input',e=>{$('char-count').textContent=e.target.value.length.toLocaleString('zh-Hant')+' 字';});
  $('example-btn').addEventListener('click',loadDemo);$('empty-example-btn').addEventListener('click',loadDemo);
  document.querySelectorAll('.tab').forEach(b=>b.addEventListener('click',()=>showTab(b.dataset.tab)));
  $('edit-toggle').addEventListener('change',e=>setEditable(e.target.checked));
  $('print-btn').addEventListener('click',printNow);
  $('html-btn').addEventListener('click',()=>{if(!state.result)return;downloadBlob(new Blob([documentHTML()],{type:'text/html;charset=utf-8'}),'EF_'+safeName(state.result.title)+'.html');});
  $('word-btn').addEventListener('click',()=>{if(!state.result)return;const html=documentHTML().replace('<html lang="zh-Hant">','<html lang="zh-Hant" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word">');downloadBlob(new Blob(['\ufeff',html],{type:'application/msword;charset=utf-8'}),'EF_'+safeName(state.result.title)+'.doc');});
  $('reset-btn').addEventListener('click',generate);
  $('browse-btn').addEventListener('click',e=>{e.stopPropagation();$('file-upload').click();});
  const dz=$('drop-zone');dz.addEventListener('click',()=>{$('file-upload').click();});
  dz.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();$('file-upload').click();}});
  dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('dragging');});
  dz.addEventListener('dragleave',()=>dz.classList.remove('dragging'));
  dz.addEventListener('drop',async e=>{e.preventDefault();dz.classList.remove('dragging');try{await loadFile(e.dataTransfer.files[0]);$('form-message').textContent='';}catch(err){$('file-status').classList.add('error');$('file-status').textContent=err.message;}});
  $('file-upload').addEventListener('change',async e=>{try{$('file-status').textContent='讀取中…';await loadFile(e.target.files[0]);$('form-message').textContent='';}catch(err){$('file-status').classList.add('error');$('file-status').textContent=err.message;}finally{e.target.value='';}});
  window.addEventListener('afterprint',()=>document.body.classList.remove('print-notes','print-worksheet','print-key','print-both'));
})();
