<h1><?= e($offer['title']) ?></h1>
<p class="meta"><?= e($offer['skill']) ?> &middot; <?= e($offer['category']) ?> &middot; <?= e($offer['level']) ?></p>
<p>Teacher: <strong><?= e($offer['teacher']) ?></strong></p>

<?php if ($summary && $summary['cnt'] > 0): ?>
  <p class="rating">Rating: <strong><?= number_format((float)$summary['avg_rating'], 1) ?></strong> / 5
     (<?= (int)$summary['cnt'] ?> review<?= $summary['cnt'] == 1 ? '' : 's' ?>)</p>
<?php else: ?>
  <p class="rating">No reviews yet.</p>
<?php endif; ?>

<p><?= nl2br(e($offer['description'])) ?></p>

<?php $me = current_user(); ?>
<?php if ($me && $me['id'] != $offer['teacher_id']): ?>
  <form method="post" action="<?= url('sessions/request') ?>" class="form">
    <?= csrf_field() ?>
    <input type="hidden" name="offer_id" value="<?= (int)$offer['id'] ?>">
    <label>Preferred time (optional)
      <input type="datetime-local" name="scheduled_at">
    </label>
    <button type="submit">Request session (1 credit on completion)</button>
  </form>
<?php elseif (!$me): ?>
  <p><a href="<?= url('login') ?>">Login</a> to request a session.</p>
<?php endif; ?>

<h2>Reviews</h2>
<?php if (!$reviews): ?>
  <p>Be the first to learn and review this skill.</p>
<?php else: ?>
  <?php foreach ($reviews as $rv): ?>
    <div class="card">
      <p><strong><?= str_repeat('*', (int)$rv['rating']) ?></strong>
         (<?= (int)$rv['rating'] ?>/5) by <?= e($rv['reviewer']) ?></p>
      <?php if ($rv['comment']): ?><p><?= nl2br(e($rv['comment'])) ?></p><?php endif; ?>
    </div>
  <?php endforeach; ?>
<?php endif; ?>
