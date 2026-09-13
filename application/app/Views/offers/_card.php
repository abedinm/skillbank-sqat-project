<div class="card">
  <h3><a href="<?= url('offer?id=' . (int)$offer['id']) ?>"><?= e($offer['title']) ?></a></h3>
  <p class="meta"><?= e($offer['skill']) ?> &middot; <?= e($offer['category']) ?> &middot; <?= e($offer['level']) ?></p>
  <p><?= e(mb_strimwidth($offer['description'] ?? '', 0, 120, '...')) ?></p>
  <p class="teacher">By <?= e($offer['teacher']) ?></p>
</div>
