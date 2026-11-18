from playwright.sync_api import sync_playwright
from pathlib import Path
import json
import os
url=os.environ.get('VIEWER_URL','http://127.0.0.1:18955/arken-wiki.html')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':1050});errors=[];network=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:network.append(r.url) if r.url.startswith(('http:','https:')) and not r.url.startswith('http://127.0.0.1:18955/') else None)
 page.goto(url);assert page.get_by_role('heading',name='아르켄 위키',exact=True).count()==1;assert page.locator('.stats').inner_text().startswith('75');page.screenshot(path='/tmp/arken-viewer-home.png',full_page=True)
 page.locator('#query').fill('세린');page.locator('#search button').click();assert page.locator('.result').count()>0;page.locator('.result a').filter(has_text='세린 바엘').click();assert page.locator('h1').inner_text()=='세린 바엘'
 page.locator('.body a').filter(has_text='토마 리드').click();assert page.locator('h1').inner_text()=='토마 리드';page.go_back();assert page.locator('h1').inner_text()=='세린 바엘';page.reload();assert page.locator('h1').inner_text()=='세린 바엘'
 page.locator('#rail a').first.click();assert 'section-' in page.url
 page.locator('details').click();assert 'HERO-SERIN' in page.locator('details pre').inner_text()
 with page.expect_download() as info:page.locator('#download-md').click()
 assert info.value.suggested_filename=='HERO-SERIN.md'
 page.locator('#theme').click();assert 'dark' in page.locator('body').get_attribute('class');page.locator('#theme').click()
 page.screenshot(path='/tmp/arken-viewer-article.png',full_page=True)
 page.goto(url+'#category/Item');assert page.locator('.result').count()==4
 page.goto(url+'#page/timeline');text=page.locator('.body').inner_text();assert text.index('초여름 교역 중단')<text.index('남은 물품의 임시 교환')
 # Every article and internal renderer link must resolve offline.
 count=page.evaluate('pages.length');assert count==78
 for i in range(count):
  page.evaluate('(i)=>{location.hash=link(pages[i].record)}',i);page.wait_for_function('(i)=>document.querySelector("h1").textContent===pages[i].name',arg=i)
  assert page.locator('.body').inner_text().strip()
 result=page.evaluate('markdown("## 제목\\n<img src=x onerror=alert(1)>\\n[bad](javascript:alert)\\n[세린](HERO-SERIN.md)")');assert '<img' not in result and 'href="javascript:' not in result and '#page/HERO-SERIN' in result
 page.goto(url+'#home');page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path='/tmp/arken-viewer-mobile.png',full_page=True)
 assert not errors,errors;assert not network,network
 print(json.dumps({'pages_opened':count,'external_requests':len(network),'javascript_errors':errors,'checks':['localhost-rendering','search','links','back','reload','TOC','download','theme','category','timeline','escaping','mobile']},ensure_ascii=False));b.close()
