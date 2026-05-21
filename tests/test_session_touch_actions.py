from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SESSIONS_JS = (ROOT / "static" / "sessions.js").read_text(encoding="utf-8")
STYLE_CSS = (ROOT / "static" / "style.css").read_text(encoding="utf-8")


def test_session_menu_uses_viewport_height_not_fixed_scroll_cap():
    assert "max-height:calc(100vh - 16px)" in STYLE_CSS
    session_menu = STYLE_CSS[STYLE_CSS.find(".session-action-menu{"):STYLE_CSS.find(".session-action-menu.open")]
    assert "max-height:320px" not in session_menu


def test_session_menu_has_subtle_open_animation():
    session_menu = STYLE_CSS[STYLE_CSS.find(".session-action-menu{"):STYLE_CSS.find(".session-action-menu.open")]
    assert "will-change:opacity,transform" in session_menu
    assert "transform-origin:top right" in session_menu
    assert "function _playSessionActionMenuEntrance(menu){" in SESSIONS_JS
    assert "typeof menu.animate==='function'" in SESSIONS_JS
    assert "{opacity:0, transform:'translate3d(0,-4px,0) scale(.985)'}" in SESSIONS_JS
    assert "{duration:450, easing:'cubic-bezier(.2,.8,.2,1)'}" in SESSIONS_JS
    assert "menu.classList.add('open-animated')" in SESSIONS_JS
    assert ".session-action-menu.open-animated{animation:session-menu-in .45s cubic-bezier(.2,.8,.2,1);}" in STYLE_CSS
    assert "@keyframes session-menu-in" in STYLE_CSS
    assert "@media (prefers-reduced-motion:reduce)" in STYLE_CSS
    assert ".session-action-menu{animation:none;will-change:auto;}" in STYLE_CSS
    assert ".session-item,.session-item.session-reflowing,.session-item.swipe-committed,.session-item.swipe-removing{transition:none;}" in STYLE_CSS
    assert ".session-item.long-pressing{animation:none;}" in STYLE_CSS


def test_mobile_session_menu_opens_from_long_press_and_hides_dots():
    assert "_longPressDelay=400" in SESSIONS_JS
    assert "el.classList.add('long-pressing')" in SESSIONS_JS
    assert "if(!_longPressMenuOpened) el.classList.remove('long-pressing')" in SESSIONS_JS
    assert "row.classList.remove('menu-open','long-pressing')" in SESSIONS_JS
    assert "_openSessionActionMenu(s, el)" in SESSIONS_JS
    assert "@media (hover:none) and (pointer:coarse)" in STYLE_CSS
    assert ".session-actions{display:none;}" in STYLE_CSS
    assert "const _beginSessionGesture=(clientX,clientY,pointerType='')=>{" in SESSIONS_JS
    assert "const _scheduleSessionLongPressMenu=()=>{" in SESSIONS_JS
    mobile_touch = STYLE_CSS[STYLE_CSS.find("@media (hover:none) and (pointer:coarse)"):STYLE_CSS.find("@media (max-width: 340px)")]
    assert ".session-item{padding-right:6px;}" in mobile_touch
    assert ".session-item.streaming,.session-item.unread{padding-right:40px;}" in mobile_touch
    assert ".session-item:focus-within,.session-item.menu-open{padding-right:6px;}" in mobile_touch


def test_open_session_menu_consumes_next_row_activation():
    assert "if(_sessionActionMenu&&!_sessionActionMenu.contains(target)){" in SESSIONS_JS
    assert "closeSessionActionMenu();" in SESSIONS_JS
    assert "e.stopPropagation();" in SESSIONS_JS
    assert "const stopMenuPointer=(e)=>e.stopPropagation();" in SESSIONS_JS
    assert "menuBtn.onpointerdown=stopMenuPointer;" in SESSIONS_JS
    assert "menuBtn.onpointerup=stopMenuPointer;" in SESSIONS_JS
    menu_btn_idx = SESSIONS_JS.find("menuBtn.onpointerdown=stopMenuPointer;")
    menu_click_idx = SESSIONS_JS.find("menuBtn.onclick=(e)=>{", menu_btn_idx)
    assert menu_btn_idx > 0 and menu_click_idx > menu_btn_idx
    assert "const _isSessionActionTarget=(target)=>{" in SESSIONS_JS
    assert "return !!(actions&&target&&actions.contains(target));" in SESSIONS_JS
    assert "if(_isSessionActionTarget(e.target)) return;" in SESSIONS_JS
    assert "if(_isSessionActionTarget(target)){_gestureState='idle';return false;}" in SESSIONS_JS
    assert "if(_longPressMenuOpened){_gestureState='idle';return true;}" in SESSIONS_JS
    finish_idx = SESSIONS_JS.find("const _finishSessionGesture=(clientX,clientY,target,pointerType)=>{")
    dismiss_idx = SESSIONS_JS.find("if(_sessionActionMenu&&!_sessionActionMenu.contains(target)){", finish_idx)
    load_idx = SESSIONS_JS.find("await loadSession(s.session_id)", finish_idx)
    pointerup_idx = SESSIONS_JS.find("el.onpointerup=(e)=>{")
    assert finish_idx > 0 and load_idx > finish_idx
    assert dismiss_idx > finish_idx and dismiss_idx < load_idx
    assert "if(_finishSessionGesture(e.clientX,e.clientY,e.target,e.pointerType)) e.stopPropagation();" in SESSIONS_JS[pointerup_idx:]


def test_session_swipes_archive_right_and_delete_left():
    assert "_gesturePointerType!=='mouse'" in SESSIONS_JS
    assert "_swipeTracking=true" in SESSIONS_JS
    assert "const _trackHorizontalSwipe=(dx,dy)=>{" in SESSIONS_JS
    assert "_archiveSwipeActionThreshold=128" in SESSIONS_JS
    assert "_deleteSwipeActionThreshold=128" in SESSIONS_JS
    assert "_committedSwipeDuration=_sessionPrefersReducedMotion()?0:420" in SESSIONS_JS
    assert "const _handleSessionSwipe=(signedDx,signedDy)=>{" in SESSIONS_JS
    assert "const actionThreshold=signedDx>0?_archiveSwipeActionThreshold:_deleteSwipeActionThreshold;" in SESSIONS_JS
    assert "if(Math.abs(signedDx)<actionThreshold) return false;" in SESSIONS_JS
    assert "const _updateSessionGesture=(clientX,clientY)=>{" in SESSIONS_JS
    assert "if(_isSessionSwipeTarget()&&(_swipeTracking||dx>dy)) _paintSessionSwipe(signedDx)" in SESSIONS_JS
    assert "_updateSessionGesture(e.clientX,e.clientY);" in SESSIONS_JS
    assert "if(_updateSessionGesture(touch.clientX,touch.clientY)) e.preventDefault();" in SESSIONS_JS
    assert "_beginSessionGesture(touch.clientX,touch.clientY,'touch');" in SESSIONS_JS
    assert "if(signedDx>0){" in SESSIONS_JS
    assert "_archiveSession(s,!s.archived)" in SESSIONS_JS
    assert "deleteSession(s.session_id,async()=>{" in SESSIONS_JS
    delete_branch_start = SESSIONS_JS.find("}else if(_canSwipeDeleteSession()){")
    delete_branch_end = SESSIONS_JS.find("}else if(typeof showToast", delete_branch_start)
    assert delete_branch_start >= 0 and delete_branch_end > delete_branch_start
    delete_branch = SESSIONS_JS[delete_branch_start:delete_branch_end]
    delete_call_idx = delete_branch.find("deleteSession(s.session_id,async()=>{")
    delete_complete_idx = delete_branch.find("_completeSessionSwipePaint(signedDx);")
    assert delete_call_idx > 0 and delete_complete_idx > delete_call_idx
    assert "const completedAt=Date.now();" not in delete_branch
    assert "showToast('Imported sessions cannot be deleted here.',3000);" in SESSIONS_JS
    assert "let _gestureState='idle';" in SESSIONS_JS
    assert "_gestureState='dragging';" in SESSIONS_JS
    assert "const _promoteSessionDrag=(dx,dy)=>{" in SESSIONS_JS
    assert "const _commitSessionSwipe=()=>{" in SESSIONS_JS
    assert "_commitSessionSwipe();" in SESSIONS_JS
    assert "const wasDragging=_gestureState==='dragging'||_swipeTracking;" in SESSIONS_JS
    assert "if(_gestureState==='committed'){" in SESSIONS_JS
    assert SESSIONS_JS.count("if(e.pointerType==='touch') return;") >= 3
    assert "el.onpointercancel=(e)=>{" in SESSIONS_JS
    assert "if(e.pointerType==='touch') return;" in SESSIONS_JS
    assert "if(_gesturePointerType==='mouse'&&_gestureState!=='idle') _clearPointerDragState();" in SESSIONS_JS


def test_session_swipes_show_visual_feedback_and_touch_load_clears():
    assert "const _paintSessionSwipe=(signedDx)=>{" in SESSIONS_JS
    assert "const rawOffset=signedDx*.55" in SESSIONS_JS
    assert "const revealedOffset=Math.max(-72,Math.min(72,rawOffset))" in SESSIONS_JS
    assert "const overshoot=Math.max(0,Math.abs(rawOffset)-72)" in SESSIONS_JS
    assert "Math.sqrt(overshoot)*5" in SESSIONS_JS
    assert "el.style.setProperty('--session-swipe-offset',offset+'px')" in SESSIONS_JS
    assert "const reveal=Math.min(132,Math.max(36,Math.abs(rawOffset)+24));" in SESSIONS_JS
    assert "const iconScale=1+Math.min(.45,Math.max(0,Math.abs(rawOffset)-52)/130);" in SESSIONS_JS
    assert "el.style.setProperty('--session-swipe-reveal',reveal+'px')" in SESSIONS_JS
    assert "el.style.setProperty('--session-swipe-icon-scale',iconScale)" in SESSIONS_JS
    assert "const progress=Math.min(1,Math.abs(revealedOffset)/72)" in SESSIONS_JS
    assert "el.style.setProperty('--session-swipe-progress',Math.pow(progress,1.5))" in SESSIONS_JS
    assert "const _clearSessionSwipePaint=()=>{" in SESSIONS_JS
    assert "el.style.removeProperty('--session-swipe-reveal');" in SESSIONS_JS
    assert "el.style.removeProperty('--session-swipe-icon-scale');" in SESSIONS_JS
    assert "el.style.removeProperty('height');" in SESSIONS_JS
    assert "el.style.removeProperty('min-height');" in SESSIONS_JS
    assert "el.classList.remove('swiping-right','swiping-left','swipe-committed','swipe-removing')" in SESSIONS_JS
    assert "const _settleSessionSwipePaint=()=>{" in SESSIONS_JS
    assert "const _completeSessionSwipePaint=(signedDx)=>{" in SESSIONS_JS
    assert "el.classList.remove('dragging');" in SESSIONS_JS
    assert "el.classList.add('swipe-committed')" in SESSIONS_JS
    assert "el.style.height=rect.height+'px'" in SESSIONS_JS
    assert "requestAnimationFrame(()=>el.classList.add('swipe-removing'))" in SESSIONS_JS
    assert "el.style.setProperty('--session-swipe-progress','0')" in SESSIONS_JS
    assert "deleteSession(s.session_id,async()=>{" in SESSIONS_JS
    assert "const archived=await _archiveSession(s,!s.archived);" in SESSIONS_JS
    assert "if(!archived) _settleSessionSwipePaint();" in SESSIONS_JS
    assert "await new Promise(resolve=>setTimeout(resolve,_committedSwipeDuration));" in SESSIONS_JS
    assert "async function deleteSession(sid, beforeDelete=null){" in SESSIONS_JS
    assert "if(beforeDelete) await beforeDelete();" in SESSIONS_JS
    assert "requestAnimationFrame(()=>requestAnimationFrame(_clearSessionSwipePaint))" in SESSIONS_JS
    assert ".session-item.swiping-right" in STYLE_CSS
    assert ".session-item.swiping-left" in STYLE_CSS
    assert "const _makeSessionSwipeAffordance=(side,icon,label)=>{" in SESSIONS_JS
    assert "affordance.setAttribute('aria-hidden','true');" in SESSIONS_JS
    assert "_makeSessionSwipeAffordance('right',s.archived?'undo':'archive',s.archived?'Restore':t('session_batch_archive'))" in SESSIONS_JS
    assert "_makeSessionSwipeAffordance('left','trash-2'" in SESSIONS_JS
    assert ".session-swipe-affordance{" in STYLE_CSS
    assert "opacity:var(--session-swipe-progress,0)" in STYLE_CSS
    assert "width:var(--session-swipe-reveal,0px)" in STYLE_CSS
    assert ".session-item.swiping-right{background:color-mix(in srgb,var(--warning) 16%,var(--surface));box-shadow:0 0 0 1px color-mix(in srgb,var(--warning) 48%,transparent);}" in STYLE_CSS
    assert ".session-item.swiping-left{background:color-mix(in srgb,var(--error) 14%,var(--surface));box-shadow:0 0 0 1px color-mix(in srgb,var(--error) 48%,transparent);}" in STYLE_CSS
    assert "background:var(--warning)" in STYLE_CSS
    assert ".session-item.archived .session-swipe-affordance-right{background:var(--success);}" in STYLE_CSS
    assert ".session-item.archived.dragging.swiping-right" in STYLE_CSS
    assert ".session-item.active.archived.swiping-right{background:color-mix(in srgb,var(--success) 20%,var(--accent-bg));}" in STYLE_CSS
    assert "background:var(--error)" in STYLE_CSS
    assert ".session-item.swiping-right .session-swipe-affordance-right" in STYLE_CSS
    assert ".session-item.swiping-left .session-swipe-affordance-left" in STYLE_CSS
    assert "transform:translateX(calc(-1 * var(--session-swipe-offset,0px))) scale(calc(.82 + var(--session-swipe-progress,0) * .18))" in STYLE_CSS
    assert ".session-swipe-badge{" in STYLE_CSS
    assert "transform:scaleX(var(--session-swipe-icon-scale,1))" in STYLE_CSS
    assert ".session-swipe-label{" in STYLE_CSS
    assert "transform .5s cubic-bezier(.2,.8,.2,1)" in STYLE_CSS
    assert ".session-item.dragging.swiping-right" in STYLE_CSS
    assert ".session-item.dragging.swiping-left" in STYLE_CSS
    assert ".session-item.dragging{transition:background .15s,color .15s,box-shadow .15s ease;}" in STYLE_CSS
    assert ".session-item.swipe-committed" in STYLE_CSS
    assert ".session-item.swipe-removing{" in STYLE_CSS
    assert "height .36s cubic-bezier(.2,.8,.2,1)" in STYLE_CSS
    assert "transform .42s cubic-bezier(.2,.8,.2,1)" in STYLE_CSS
    assert ".session-item.swipe-committed .session-swipe-affordance{transition:opacity .18s ease,transform .18s ease;}" in STYLE_CSS
    assert ".session-item.long-pressing" in STYLE_CSS
    assert "@keyframes session-long-press" in STYLE_CSS
    assert "transform:translateX(var(--session-swipe-offset,0))" in STYLE_CSS
    assert "finally{" in SESSIONS_JS
    assert "el.classList.remove('loading');" in SESSIONS_JS


def test_session_removal_reflows_surviving_rows_smoothly():
    assert "let _pendingSessionReflowPositions = null;" in SESSIONS_JS
    assert "function _captureSessionReflowPositions(){" in SESSIONS_JS
    assert "positions.set(row.dataset.sid,row.getBoundingClientRect().top);" in SESSIONS_JS
    assert "function _playQueuedSessionReflowAnimation(){" in SESSIONS_JS
    assert "function _sessionPrefersReducedMotion(){" in SESSIONS_JS
    assert "const delta=oldTop-row.getBoundingClientRect().top;" in SESSIONS_JS
    assert "row.style.setProperty('--session-reflow-offset',delta+'px')" in SESSIONS_JS
    assert "row.classList.add('session-reflowing')" in SESSIONS_JS
    assert "row.style.setProperty('--session-reflow-offset','0px')" in SESSIONS_JS
    assert "const reflowPositions=_captureSessionReflowPositions();" in SESSIONS_JS
    assert SESSIONS_JS.count("_pendingSessionReflowPositions=reflowPositions;") >= 2
    assert "_playQueuedSessionReflowAnimation();" in SESSIONS_JS
    assert ".session-item.session-reflowing{transition:background .15s,color .15s,transform .36s cubic-bezier(.2,.8,.2,1),box-shadow .15s ease;will-change:transform;}" in STYLE_CSS


def test_ios_touch_events_drive_session_swipes():
    assert "el.addEventListener('touchstart'" in SESSIONS_JS
    assert "el.addEventListener('touchmove'" in SESSIONS_JS
    assert "el.addEventListener('touchcancel',_clearPointerDragState" in SESSIONS_JS
    assert "el.addEventListener('touchend'" in SESSIONS_JS
    assert "const _finishSessionGesture=(clientX,clientY,target,pointerType)=>{" in SESSIONS_JS
    assert "{passive:false}" in SESSIONS_JS
    assert "if(_updateSessionGesture(touch.clientX,touch.clientY)) e.preventDefault();" in SESSIONS_JS
    assert SESSIONS_JS.count("if(e.pointerType==='touch') return;") >= 3
    assert "if(_finishSessionGesture(touch.clientX,touch.clientY,e.target,'touch')) e.stopPropagation();" in SESSIONS_JS
    assert "window.PointerEvent" not in SESSIONS_JS


def test_touch_session_rows_preserve_vertical_scroll():
    assert ".session-item{padding:8px 8px;" in STYLE_CSS
    item_rule = STYLE_CSS[STYLE_CSS.find(".session-item{padding:8px 8px;"):STYLE_CSS.find("}", STYLE_CSS.find(".session-item{padding:8px 8px;"))]
    assert "touch-action:pan-y" in item_rule
    assert "user-select:none" in item_rule
    assert "-webkit-user-select:none" in item_rule
    assert "-webkit-touch-callout:none" in item_rule
