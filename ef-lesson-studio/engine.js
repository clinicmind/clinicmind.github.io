/* Hill · Skill · Will | Copyright 2026. Original, transparent browser-side transformation. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.EFEngine = api;
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const COMMON = new Set(('我們 你們 他們 這些 那些 一個 一種 一些 其中 中的 一部分 另一部分 這一部分 同時 另外 可以 因為 所以 但是 然而 以及 並且 透過 進行 就是 具有 相關 方式 方法 時候 此外 例如 例如說 一定 需要 不是 可能 主要 這個 那個 是否 若果 也是 還有 能夠 之後 以前 已經 由於 必須 學生 老師 教師 課文 內容 問題 答案 應該 請問 自己 了解 理解 過程 使用 學習 研究 發現 結果 分析 影響 事情 很多 不同 兩個 三個 這裡 上述 以下 常見 重要 第一 第二 第三 這種 各種 有些 其他 其中 因此 通常 有時').split(' '));
  const BAD_TAIL = /[，。；、：！？?！70-\u036f]$/;
  const CJK = /[\u3400-\u9fff]/;
  const HTML_ESCAPE = {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'};
  const escapeHTML = (s) => String(s ?? '').replace(/[&<>"']/g, c => HTML_ESCAPE[c]);

  function normalizeText(s) {
    return String(s || '')
      .replace(/\r\n?/g, '\n').replace(/\u00a0/g, ' ').replace(/\u200b/g,'')
      .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,'')
      .replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,'')
      .replace(/<[^>]+>/g, ' ')
      .replace(/^\s{0,3}#{1,6}\s+/gm,'')
      .replace(/^\s{0,3}[-*]\s+/gm,'')
      .replace(/[ \t]+/g,' ')
      .replace(/\n[ \t]+/g,'\n')
      .replace(/\n{4,}/g,'\n\n\n').trim();
  }
  function sentencesFromText(text) {
    let normalized=normalizeText(text);
    let parts=normalized.split(/(?<=[。！？!?；;])\s*|\n+/u).map(x=>x.trim()).filter(Boolean);
    let out=[];
    for(let p of parts){
      if(p.length>175) {
        const bits=p.split(/(?<=[，,])\s*/u);
        let accum='';
        for(const bit of bits){if(accum.length+bit.length>132&&accum.length>25){out.push(accum);accum='';}accum+=bit;}
        if(accum)out.push(accum);
      } else out.push(p);
    }
    return out.filter(x=>x.length>=12 && /[\p{L}\p{N}]/u.test(x)).slice(0,650);
  }
  function tokens(text){
    let output=[];
    if(typeof Intl!=='undefined'&&Intl.Segmenter){
      let seg=new Intl.Segmenter('zh-Hant',{granularity:'word'});
      for(const item of seg.segment(text)){
        let s=item.segment.trim();
        if(item.isWordLike && s.length>=2&&s.length<=13&& !COMMON.has(s) && /[\p{L}\p{N}]/u.test(s))output.push(s);
      }
    }
    if(output.length<3) {
      const units=text.match(/[\u3400-\u9fff]{2,10}|[A-Za-z][A-Za-z0-9-]{2,}/g)||[];
      output.push(...units.filter(x=>!COMMON.has(x)));
    }
    return output;
  }
  function extractKeywords(text, max=15){
    const freq=new Map();
    const units=tokens(text);
    for(const token of units){
      const word=token.trim().replace(/[，。！？；、:：\s]+/g,'');
      if(word.length<2||word.length>12||COMMON.has(word)||/^\d+$/.test(word))continue;
      let score=(freq.get(word)||0)+1;
      freq.set(word,score);
    }
    let words=[...freq].map(([w,f])=>({word:w,score:f+Math.min(w.length,5)*0.055+(CJK.test(w)?0.2:0)}));
    words.sort((a,b)=>b.score-a.score || b.word.length-a.word.length);
    const selected=[];
    for(const row of words){
      if(selected.some(x=>x.includes(row.word)&&x!==row.word))continue;
      selected.push(row.word);
      if(selected.length>=max)break;
    }
    return selected;
  }
  function cleanSentence(s){return s.replace(/^\s*[\d一二三四五六七八九十]+[.、)]\s*/u,'').trim();}
  function chooseSentences(text,count){
    const all=sentencesFromText(text).map(cleanSentence);
    const seen=new Set(),candidates=all.filter(s=>{
      if(s.length<19||s.length>165||s.includes('http://')||s.includes('https://'))return false;
      const key=s.slice(0,30);if(seen.has(key))return false;seen.add(key);return true;
    });
    if(candidates.length<=count)return candidates;
    // Even sampling preserves narrative progression; it does not invent or reorder source claims.
    let pick=[];
    for(let i=0;i<count;i++){
      let idx=Math.min(candidates.length-1,Math.round(i*(candidates.length-1)/(count-1||1)));
      if(!pick.includes(idx))pick.push(idx);
    }
    return pick.map(i=>candidates[i]);
  }
  function makeCloze(sentence,keywords,level='standard',index=0){
    const ranked=keywords.filter(x=>sentence.includes(x)&&x.length>=2&&x.length<=12);
    const words=tokens(sentence).filter(w=>w.length>=2&&w.length<=12 && !COMMON.has(w));
    let answer=ranked.find(x=>sentence.includes(x));
    if(!answer)answer=words.find(x=>sentence.includes(x))||'';
    if(!answer){return {html:escapeHTML(sentence),answer:'',source:sentence,blanked:false,index};}
    const at=sentence.indexOf(answer);
    const placeholder=level==='low'? '＿＿＿＿＿＿＿＿' :'＿＿＿＿＿＿';
    const html=escapeHTML(sentence.slice(0,at))+'<span class="blank">'+placeholder+'</span>'+escapeHTML(sentence.slice(at+answer.length));
    return {html,answer,source:sentence,blanked:true,index};
  }
  function outputCount(grade,scaffold){
    const base=grade==='p1'?4:grade==='p2'?5:grade==='s1'?7:8;
    return Math.max(3,Math.min(10,base+(scaffold==='high'?-1:scaffold==='low'?2:0)));
  }
  function promptsFor(subject,grade){
    let prompts={
      chinese:['哪一句最能表達文章的重點？請抄下關鍵字並說明理由。','找出一個支持作者想法的例子或細節，註明原文位置。'],
      english:['Circle the key idea in the passage and explain it in your own words.','Find one detail from the text that supports the main idea.'],
      math:['從題目找出「已知、要求、限制」，並用圖或表整理。','選一種解法，完成後檢查數值、單位和答案是否合理。'],
      science:['找出課文中的一個概念及其解釋，畫出它們的關係。','指出一項原因、過程或結果，並標明原文的依據。'],
      humanities:['找出課文提及的一個事件、主張或現象，整理其要點。','比較兩個觀點或因素；如果課文沒有第二個，請寫明「未提供」。'],
      other:['從課文找出最重要的一項資訊，註明原文依據。','用自己的話說出這項資訊與其他內容的關係。']
    };
    const p=prompts[subject]||prompts.other;
    if(grade==='p1')return ['圈出你覺得最重要的一句，向同學說說理由。','從課文找一個例子，畫圖或口頭分享。'];
    return p;
  }
  function choicesFor(subject){
    if(subject==='math')return ['算式＋檢查','步驟圖','口頭講解'];
    if(subject==='science')return ['流程圖','因果箭嘴圖','三句摘要'];
    if(subject==='humanities')return ['比較表','時間線','三句摘要'];
    if(subject==='english')return ['concept map','short summary','oral explanation'];
    return ['概念圖','三句摘要','向同學解說'];
  }
  function build(input){
    const config={grade:'p2',subject:'chinese',scaffold:'standard',worksheetTitle:'',goal:'',...input};
    const text=normalizeText(config.text);
    const count=outputCount(config.grade,config.scaffold);
    const all=sentencesFromText(text);
    if(text.length<75||all.length<2)throw new Error('課文內容太少：請至少提供約 75 個字、兩句以上可閱讀的課文。');
    if(text.length>120000)throw new Error('課文超過 120,000 字。請先分章或分節處理，避免輸出過長。');
    const topic=(config.worksheetTitle||'').trim() || (text.split('\n').find(x=>x.trim().length>=2&&x.trim().length<=34)||'課文學習').replace(/[。！?？]$/,'').slice(0,38);
    const manual=(config.keywords||'').split(/[、，,;；\n]+/).map(x=>x.trim()).filter(x=>x.length>=2&&x.length<=25);
    const keywords=[...new Set([...manual,...extractKeywords(text,16)])].slice(0,22);
    const chosen=chooseSentences(text,count);
    const cloze=chosen.map((sentence,index)=>makeCloze(sentence,keywords,config.scaffold,index+1));
    const actual=cloze.filter(x=>x.blanked).length;
    const banks=config.scaffold!=='low'?[...new Set(cloze.filter(x=>x.blanked).map(x=>x.answer))].sort((a,b)=>a.localeCompare(b,'zh-Hant')):[];
    const goal=(config.goal||'').trim()||`我能找出《${topic.slice(0,18)}》中的重要資訊，並運用一項策略整理與檢查自己的理解。`;
    const questions=promptsFor(config.subject,config.grade);
    const choices=choicesFor(config.subject);
    let flags=[];
    if(chosen.length<count)flags.push('課文較短：填空題數少於預設，請檢查是否已包含完整段落。');
    if(actual<Math.max(3,Math.round(chosen.length*.65)))flags.push('部分句子沒有可識別的填空詞，請於預覽中手動修改。');
    if(config.subject==='math'&&text.length<220)flags.push('數學題材較短：建議檢查題目條件與單位是否完整。');
    return {title:topic,goal,keywords,cloze,banks,questions,choices,sourceLength:text.length,sentenceCount:all.length,mode:config.mode||'both',grade:config.grade,subject:config.subject,scaffold:config.scaffold,flags,generatedAt:new Date().toISOString()};
  }
  return {normalizeText,sentencesFromText,extractKeywords,chooseSentences,makeCloze,outputCount,build,escapeHTML};
}));
