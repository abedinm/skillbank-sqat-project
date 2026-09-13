<h1>Browse skills</h1>

<input type="text" id="searchBox" class="search"
       placeholder="Search skills (e.g. Python, Guitar, Design)...">

<div id="results">
  <?php foreach ($offers as $offer): ?>
    <?php require APP . '/Views/offers/_card.php'; ?>
  <?php endforeach; ?>
</div>

<script>
  const box = document.getElementById('searchBox');
  const results = document.getElementById('results');
  box.addEventListener('input', function () {
    fetch('<?= url('search') ?>?q=' + encodeURIComponent(box.value))
      .then(r => r.text())
      .then(html => { results.innerHTML = html; });
  });
</script>
