document.addEventListener('DOMContentLoaded', () => {
    // PWA Service Worker Registration
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js')
                .then(reg => console.log('PRICVYT Service Worker registrado:', reg.scope))
                .catch(err => console.warn('Error al registrar Service Worker:', err));
        });
    }

    // PWA Installation Prompt Handle
    let deferredPrompt = null;
    const pwaInstallBtn = document.getElementById('pwaInstallBtn');
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        if (pwaInstallBtn) pwaInstallBtn.classList.remove('hidden');
    });

    if (pwaInstallBtn) {
        pwaInstallBtn.addEventListener('click', async () => {
            if (!deferredPrompt) return;
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            if (outcome === 'accepted') {
                showToast('PRICVYT instalada correctamente', 'success');
            }
            deferredPrompt = null;
            pwaInstallBtn.classList.add('hidden');
        });
    }

    // Navigation & Views
    const navItems = document.querySelectorAll('.m3-nav-item');
    const tabViews = document.querySelectorAll('.m3-tab-view');

    function switchView(targetId) {
        navItems.forEach(item => {
            if (item.dataset.target === targetId) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        tabViews.forEach(view => {
            if (view.id === targetId) {
                view.classList.add('active');
            } else {
                view.classList.remove('active');
            }
        });

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    navItems.forEach(item => {
        item.addEventListener('click', () => switchView(item.dataset.target));
    });

    // Toast Notifications System
    function showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `m3-toast m3-toast-${type}`;

        let iconName = 'info';
        if (type === 'success') iconName = 'check_circle';
        if (type === 'error') iconName = 'warning';

        toast.innerHTML = `<span class="material-symbols-outlined">${iconName}</span> <span>${message}</span>`;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-10px)';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // Search Bar & Filter Chips
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    const pasteSearchBtn = document.getElementById('pasteSearchBtn');
    const searchChips = document.querySelectorAll('.m3-chip');
    
    const searchFeedTitle = document.getElementById('searchFeedTitle');
    const searchResultCount = document.getElementById('searchResultCount');
    const searchResultsFeed = document.getElementById('searchResultsFeed');
    const searchSkeletonFeed = document.getElementById('searchSkeletonFeed');
    const searchEmptyState = document.getElementById('searchEmptyState');

    let searchTimeout = null;

    // Paste Action
    if (pasteSearchBtn) {
        pasteSearchBtn.addEventListener('click', async () => {
            try {
                const text = await navigator.clipboard.readText();
                if (text) {
                    searchInput.value = text.trim();
                    toggleSearchButtons();
                    showToast('Texto pegado del portapapeles', 'success');
                    handleSearchTrigger();
                }
            } catch (err) {
                showToast('Usa el teclado para pegar la URL', 'info');
            }
        });
    }

    // Clear Action
    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', () => {
            searchInput.value = '';
            toggleSearchButtons();
            performSearch('tendencias');
        });
    }

    searchInput.addEventListener('input', () => {
        toggleSearchButtons();
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (searchInput.value.trim().length >= 2) {
                handleSearchTrigger();
            }
        }, 600);
    });

    function toggleSearchButtons() {
        if (searchInput.value.trim().length > 0) {
            clearSearchBtn.classList.remove('hidden');
        } else {
            clearSearchBtn.classList.add('hidden');
        }
    }

    // Filter Chips Event
    searchChips.forEach(chip => {
        chip.addEventListener('click', () => {
            searchChips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            const query = chip.dataset.query;
            searchInput.value = '';
            toggleSearchButtons();
            performSearch(query);
        });
    });

    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        handleSearchTrigger();
    });

    function handleSearchTrigger() {
        const val = searchInput.value.trim();
        if (!val) return;

        // Si el usuario pegó una URL directa de YouTube, redirigir a analizador
        if (val.includes('youtube.com') || val.includes('youtu.be')) {
            analyzeDirectUrl(val);
            switchView('viewDirect');
        } else {
            switchView('viewSearch');
            performSearch(val);
        }
    }

    // Backend Search API Call
    async function performSearch(query) {
        searchSkeletonFeed.classList.remove('hidden');
        searchResultsFeed.classList.add('hidden');
        searchEmptyState.classList.add('hidden');

        searchFeedTitle.innerHTML = `<span class="material-symbols-outlined">search</span> Resultados para "${query}"`;

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&limit=15`);
            const data = await response.json();

            if (response.ok && data.status === 'success') {
                renderSearchFeed(data.results);
            } else {
                showToast(data.message || 'Error al buscar videos', 'error');
                showEmptySearch();
            }
        } catch (err) {
            console.error('Error de búsqueda:', err);
            showToast('Problema de conexión con el servidor', 'error');
            showEmptySearch();
        } finally {
            searchSkeletonFeed.classList.add('hidden');
        }
    }

    function showEmptySearch() {
        searchResultCount.textContent = '0 videos';
        searchResultsFeed.innerHTML = '';
        searchEmptyState.classList.remove('hidden');
        searchResultsFeed.classList.remove('hidden');
    }

    // Render Video Cards Feed (NO VIDEO PLAYER)
    function renderSearchFeed(results) {
        searchResultsFeed.innerHTML = '';
        if (!results || results.length === 0) {
            showEmptySearch();
            return;
        }

        searchResultCount.textContent = `${results.length} videos`;
        searchEmptyState.classList.add('hidden');
        searchResultsFeed.classList.remove('hidden');

        results.forEach(video => {
            const card = document.createElement('div');
            card.className = 'm3-video-card';
            
            card.innerHTML = `
                <div class="m3-card-thumb-wrapper">
                    <img src="${video.thumbnail}" alt="${video.title}" loading="lazy">
                    <span class="m3-badge-duration">${video.duration_str}</span>
                </div>
                <div class="m3-card-body">
                    <h3 class="m3-card-title">${video.title}</h3>
                    <div class="m3-card-meta">
                        <span class="m3-channel-name"><span class="material-symbols-outlined">account_circle</span> ${video.uploader}</span>
                        <span class="m3-views-count"><span class="material-symbols-outlined">visibility</span> ${video.view_count_str}</span>
                    </div>
                    <div class="m3-card-actions">
                        <button type="button" class="m3-btn-download-trigger" data-url="${video.url}">
                            <span class="material-symbols-outlined">download</span> Descargar Video
                        </button>
                        <button type="button" class="m3-btn-audio-trigger" data-url="${video.url}">
                            <span class="material-symbols-outlined">music_note</span> MP3
                        </button>
                    </div>
                </div>
            `;

            // Download Trigger Handlers (Open M3 Bottom Sheet directly without player)
            card.querySelector('.m3-btn-download-trigger').addEventListener('click', () => {
                openDownloadBottomSheet(video.url, 'video');
            });
            card.querySelector('.m3-btn-audio-trigger').addEventListener('click', () => {
                openDownloadBottomSheet(video.url, 'audio');
            });

            searchResultsFeed.appendChild(card);
        });
    }

    // VIEW 2: Direct Link Analyzer
    const directUrlForm = document.getElementById('directUrlForm');
    const directVideoUrl = document.getElementById('directVideoUrl');
    const directPasteBtn = document.getElementById('directPasteBtn');
    const directAnalyzeBtn = document.getElementById('directAnalyzeBtn');
    const directResultCard = document.getElementById('directResultCard');

    if (directPasteBtn) {
        directPasteBtn.addEventListener('click', async () => {
            try {
                const text = await navigator.clipboard.readText();
                if (text) {
                    directVideoUrl.value = text.trim();
                    showToast('Enlace pegado', 'success');
                }
            } catch (err) {
                showToast('Usa el teclado para pegar', 'info');
            }
        });
    }

    if (directUrlForm) {
        directUrlForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const url = directVideoUrl.value.trim();
            if (url) analyzeDirectUrl(url);
        });
    }

    async function analyzeDirectUrl(url) {
        const spinner = directAnalyzeBtn.querySelector('.m3-spinner');
        const content = directAnalyzeBtn.querySelector('.btn-content');

        content.classList.add('hidden');
        spinner.classList.remove('hidden');
        directAnalyzeBtn.disabled = true;

        try {
            openDownloadBottomSheet(url, 'video');
        } catch (err) {
            showToast('Error al analizar la URL', 'error');
        } finally {
            content.classList.remove('hidden');
            spinner.classList.add('hidden');
            directAnalyzeBtn.disabled = false;
        }
    }

    // M3 Bottom Sheet Modal logic (Direct format downloader without player)
    const bottomSheetOverlay = document.getElementById('bottomSheetOverlay');
    const closeBottomSheetBtn = document.getElementById('closeBottomSheetBtn');
    
    const sheetThumbnail = document.getElementById('sheetThumbnail');
    const sheetDuration = document.getElementById('sheetDuration');
    const sheetTitle = document.getElementById('sheetTitle');
    const sheetAuthor = document.getElementById('sheetAuthor');

    const sheetTabVideo = document.getElementById('sheetTabVideo');
    const sheetTabAudio = document.getElementById('sheetTabAudio');
    const sheetVideoFormats = document.getElementById('sheetVideoFormats');
    const sheetAudioFormats = document.getElementById('sheetAudioFormats');

    const sheetDownloadBtn = document.getElementById('sheetDownloadBtn');
    const sheetDownloadText = document.getElementById('sheetDownloadText');
    const sheetSpinner = document.getElementById('sheetSpinner');

    const sheetProgressContainer = document.getElementById('sheetProgressContainer');
    const sheetProgressStatus = document.getElementById('sheetProgressStatus');
    const sheetProgressPercent = document.getElementById('sheetProgressPercent');
    const sheetProgressBarFill = document.getElementById('sheetProgressBarFill');
    const sheetProgressDetails = document.getElementById('sheetProgressDetails');
    const sheetCancelBtn = document.getElementById('sheetCancelBtn');

    let currentSheetVideoData = null;
    let selectedSheetFormatId = null;
    let isSheetAudioMode = false;
    let sheetProgressInterval = null;
    let activeSheetDownloadId = null;

    closeBottomSheetBtn.addEventListener('click', closeBottomSheet);
    bottomSheetOverlay.addEventListener('click', (e) => {
        if (e.target === bottomSheetOverlay) closeBottomSheet();
    });

    function closeBottomSheet() {
        bottomSheetOverlay.classList.add('hidden');
    }

    sheetTabVideo.addEventListener('click', () => switchSheetTab('video'));
    sheetTabAudio.addEventListener('click', () => switchSheetTab('audio'));

    function switchSheetTab(type) {
        if (type === 'audio') {
            isSheetAudioMode = true;
            sheetTabAudio.classList.add('active');
            sheetTabVideo.classList.remove('active');
            sheetVideoFormats.classList.add('hidden');
            sheetAudioFormats.classList.remove('hidden');
            const first = sheetAudioFormats.querySelector('.m3-format-card');
            if (first) first.click();
        } else {
            isSheetAudioMode = false;
            sheetTabVideo.classList.add('active');
            sheetTabAudio.classList.remove('active');
            sheetAudioFormats.classList.add('hidden');
            sheetVideoFormats.classList.remove('hidden');
            const first = sheetVideoFormats.querySelector('.m3-format-card');
            if (first) first.click();
        }
    }

    async function openDownloadBottomSheet(url, initialType = 'video') {
        bottomSheetOverlay.classList.remove('hidden');
        sheetTitle.textContent = 'Analizando video de YouTube...';
        sheetAuthor.textContent = 'Cargando formatos...';
        sheetThumbnail.src = '';
        sheetDuration.textContent = '00:00';
        sheetVideoFormats.innerHTML = '<p class="m3-body-small">Extrayendo resoluciones HD...</p>';
        sheetAudioFormats.innerHTML = '<p class="m3-body-small">Extrayendo bitrates de audio...</p>';
        sheetProgressContainer.classList.add('hidden');
        sheetDownloadBtn.disabled = true;

        try {
            const res = await fetch('/api/info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            });

            const result = await res.json();
            if (res.ok && result.status === 'success') {
                currentSheetVideoData = result.data;
                renderSheetData(currentSheetVideoData, initialType);
                sheetDownloadBtn.disabled = false;
            } else {
                showToast(result.message || 'No se pudo obtener información del video', 'error');
                closeBottomSheet();
            }
        } catch (e) {
            showToast('Error al conectar con el servidor', 'error');
            closeBottomSheet();
        }
    }

    function renderSheetData(data, initialType) {
        sheetThumbnail.src = data.thumbnail;
        sheetDuration.textContent = data.duration_str;
        sheetTitle.textContent = data.title;
        sheetAuthor.textContent = `${data.uploader} • ${data.view_count_str} vistas`;

        renderFormatGrid(data.video_formats, sheetVideoFormats, false);
        renderFormatGrid(data.audio_formats, sheetAudioFormats, true);

        switchSheetTab(initialType);
    }

    function renderFormatGrid(formats, container, isAudio) {
        container.innerHTML = '';
        if (!formats || formats.length === 0) {
            container.innerHTML = '<p class="m3-body-small">Sin formatos disponibles</p>';
            return;
        }

        formats.forEach((fmt, index) => {
            const card = document.createElement('div');
            card.className = `m3-format-card ${index === 0 ? 'selected' : ''}`;
            card.dataset.formatId = fmt.format_id;

            if (index === 0) selectedSheetFormatId = fmt.format_id;

            card.innerHTML = `
                <span class="m3-format-res">${fmt.quality_label || fmt.resolution}</span>
                <span class="m3-format-size">${fmt.ext.toUpperCase()} • ${fmt.filesize_str}</span>
            `;

            card.addEventListener('click', () => {
                container.querySelectorAll('.m3-format-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                selectedSheetFormatId = fmt.format_id;
            });

            container.appendChild(card);
        });
    }

    // Trigger Download from Bottom Sheet
    sheetDownloadBtn.addEventListener('click', async () => {
        if (!currentSheetVideoData || !selectedSheetFormatId) return;

        activeSheetDownloadId = 'dl_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);
        
        setSheetLoading(true);
        startSheetProgressPolling(activeSheetDownloadId);
        showToast('Iniciando descarga multihilo...', 'info');

        // Add to active downloads in View 3
        addActiveDownloadItem(activeSheetDownloadId, currentSheetVideoData.title);

        try {
            const formData = new FormData();
            formData.append('url', currentSheetVideoData.url);
            formData.append('format_id', selectedSheetFormatId);
            formData.append('is_audio', isSheetAudioMode);
            formData.append('download_id', activeSheetDownloadId);

            const response = await fetch('/api/download', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.message || 'Error descargando archivo');
            }

            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            let filename = `${currentSheetVideoData.title}.${isSheetAudioMode ? 'mp3' : 'mp4'}`;
            
            const disposition = response.headers.get('Content-Disposition');
            if (disposition && disposition.indexOf('filename*=UTF-8\'\'') !== -1) {
                filename = decodeURIComponent(disposition.split('filename*=UTF-8\'\'')[1]);
            }

            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(downloadUrl);

            showToast('¡Descarga completada y guardada!', 'success');
            addToHistory(filename);

        } catch (err) {
            showToast(`Error: ${err.message}`, 'error');
        } finally {
            stopSheetProgressPolling();
            setSheetLoading(false);
        }
    });

    function setSheetLoading(isLoading) {
        if (isLoading) {
            sheetDownloadText.classList.add('hidden');
            sheetSpinner.classList.remove('hidden');
            sheetDownloadBtn.disabled = true;
        } else {
            sheetDownloadText.classList.remove('hidden');
            sheetSpinner.classList.add('hidden');
            sheetDownloadBtn.disabled = false;
        }
    }

    function startSheetProgressPolling(downloadId) {
        sheetProgressContainer.classList.remove('hidden');
        sheetProgressBarFill.style.width = '0%';
        sheetProgressPercent.textContent = '0%';

        if (sheetProgressInterval) clearInterval(sheetProgressInterval);

        sheetProgressInterval = setInterval(async () => {
            try {
                const res = await fetch(`/api/progress/${downloadId}`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.status === 'downloading') {
                        const percent = data.percent || 0;
                        sheetProgressBarFill.style.width = `${percent}%`;
                        sheetProgressPercent.textContent = `${percent}%`;
                        sheetProgressDetails.textContent = `${data.downloaded_str || '0 B'} • ${data.speed_str || ''}`;
                        updateActiveDownloadItem(downloadId, percent, data.speed_str);
                    } else if (data.status === 'processing') {
                        sheetProgressBarFill.style.width = '99%';
                        sheetProgressPercent.textContent = '99%';
                        sheetProgressDetails.textContent = 'Combinando pistas de alta calidad con FFmpeg...';
                    } else if (data.status === 'completed') {
                        sheetProgressBarFill.style.width = '100%';
                        sheetProgressPercent.textContent = '100%';
                        sheetProgressDetails.textContent = '¡Descarga Lista!';
                        removeActiveDownloadItem(downloadId);
                        stopSheetProgressPolling();
                    }
                }
            } catch (e) {}
        }, 350);
    }

    function stopSheetProgressPolling() {
        if (sheetProgressInterval) {
            clearInterval(sheetProgressInterval);
            sheetProgressInterval = null;
        }
    }

    if (sheetCancelBtn) {
        sheetCancelBtn.addEventListener('click', async () => {
            if (activeSheetDownloadId) {
                await fetch(`/api/cancel/${activeSheetDownloadId}`, { method: 'POST' });
                showToast('Descarga cancelada', 'info');
                removeActiveDownloadItem(activeSheetDownloadId);
                stopSheetProgressPolling();
                sheetProgressContainer.classList.add('hidden');
                setSheetLoading(false);
            }
        });
    }

    // View 3: Active Downloads & History Management
    const activeDownloadsContainer = document.getElementById('activeDownloadsContainer');
    const noActiveDownloads = document.getElementById('noActiveDownloads');
    const downloadHistoryContainer = document.getElementById('downloadHistoryContainer');
    const historyEmptyText = document.getElementById('historyEmptyText');
    const navDownloadsBadge = document.getElementById('navDownloadsBadge');

    let activeDownloadsCount = 0;

    function addActiveDownloadItem(id, title) {
        activeDownloadsCount++;
        updateNavBadge();

        if (noActiveDownloads) noActiveDownloads.classList.add('hidden');

        const item = document.createElement('div');
        item.id = `active_item_${id}`;
        item.className = 'm3-direct-card';
        item.style.marginBottom = '10px';
        item.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4 style="font-size:0.95rem; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:80%;">${title}</h4>
                <span id="speed_${id}" style="font-size:0.75rem; color:var(--md-sys-color-primary);">Iniciando...</span>
            </div>
            <div class="m3-linear-progress-track" style="margin-top:6px;">
                <div id="fill_${id}" class="m3-linear-progress-fill" style="width: 0%;"></div>
            </div>
        `;
        activeDownloadsContainer.appendChild(item);
    }

    function updateActiveDownloadItem(id, percent, speed) {
        const fill = document.getElementById(`fill_${id}`);
        const speedSpan = document.getElementById(`speed_${id}`);
        if (fill) fill.style.width = `${percent}%`;
        if (speedSpan && speed) speedSpan.textContent = `${percent}% • ${speed}`;
    }

    function removeActiveDownloadItem(id) {
        const item = document.getElementById(`active_item_${id}`);
        if (item) item.remove();

        activeDownloadsCount = Math.max(0, activeDownloadsCount - 1);
        updateNavBadge();

        if (activeDownloadsCount === 0 && noActiveDownloads) {
            noActiveDownloads.classList.remove('hidden');
        }
    }

    function updateNavBadge() {
        if (!navDownloadsBadge) return;
        if (activeDownloadsCount > 0) {
            navDownloadsBadge.textContent = activeDownloadsCount;
            navDownloadsBadge.classList.remove('hidden');
        } else {
            navDownloadsBadge.classList.add('hidden');
        }
    }

    function addToHistory(filename) {
        if (historyEmptyText) historyEmptyText.classList.add('hidden');

        const card = document.createElement('div');
        card.className = 'm3-chip';
        card.style.width = '100%';
        card.style.justifyContent = 'space-between';
        card.style.marginBottom = '6px';
        card.innerHTML = `
            <span style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:85%;"><span class="material-symbols-outlined">description</span> ${filename}</span>
            <span class="material-symbols-outlined" style="color:var(--md-sys-color-primary);">check_circle</span>
        `;
        downloadHistoryContainer.prepend(card);
    }

    // Android 13+ Share Target URL detection
    const urlParams = new URLSearchParams(window.location.search);
    const sharedUrl = urlParams.get('url') || urlParams.get('text');
    if (sharedUrl) {
        showToast('Enlace compartido recibido', 'info');
        analyzeDirectUrl(sharedUrl);
        switchView('viewDirect');
    } else {
        // Initial search load
        performSearch('tendencias');
    }
});
