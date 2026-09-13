<?php
// Small helper to render an accept/complete/cancel button as an inline POST form.
function action_btn($sessionId, $action, $label) {
    return '<form method="post" action="' . url('sessions/action') . '" class="inline-form">'
         . csrf_field()
         . '<input type="hidden" name="id" value="' . (int)$sessionId . '">'
         . '<input type="hidden" name="action" value="' . e($action) . '">'
         . '<button type="submit">' . e($label) . '</button></form>';
}
?>
<h1>My dashboard</h1>
<p class="balance">Credit balance: <strong><?= (int)$me['credits'] ?></strong>
   &nbsp;(teach to earn, learn to spend)</p>

<h2>Suggested swaps (mutual matches)</h2>
<?php if (!$matches): ?>
  <p>No mutual matches yet. Add skills to your wishlist below to find swap partners.</p>
<?php else: ?>
  <ul class="matches">
    <?php foreach ($matches as $m): ?>
      <li>Swap with <strong><?= e($m['name']) ?></strong>:
          they can teach you <strong><?= e($m['they_teach']) ?></strong>,
          you can teach them <strong><?= e($m['i_teach']) ?></strong>.</li>
    <?php endforeach; ?>
  </ul>
<?php endif; ?>

<h2>Skills I want to learn</h2>
<form method="post" action="<?= url('dashboard') ?>" class="form-inline">
  <?= csrf_field() ?>
  <select name="skill_id">
    <?php foreach ($allSkills as $s): ?>
      <option value="<?= (int)$s['id'] ?>"><?= e($s['name']) ?> (<?= e($s['category']) ?>)</option>
    <?php endforeach; ?>
  </select>
  <button type="submit" name="add_wish" value="1">Add to wishlist</button>
</form>
<table class="table">
  <tr><th>Skill</th><th>Category</th><th></th></tr>
  <?php foreach ($wishes as $w): ?>
  <tr>
    <td><?= e($w['skill']) ?></td>
    <td><?= e($w['category']) ?></td>
    <td>
      <form method="post" action="<?= url('dashboard') ?>" class="inline-form">
        <?= csrf_field() ?>
        <input type="hidden" name="wish_id" value="<?= (int)$w['id'] ?>">
        <button type="submit" name="remove_wish" value="1">Remove</button>
      </form>
    </td>
  </tr>
  <?php endforeach; ?>
</table>

<h2>My skill offers</h2>
<p><a href="<?= url('offers/create') ?>">+ Offer a new skill</a></p>
<table class="table">
  <tr><th>Title</th><th>Skill</th><th>Level</th><th>Status</th><th>Actions</th></tr>
  <?php foreach ($myOffers as $o): ?>
  <tr>
    <td><?= e($o['title']) ?></td>
    <td><?= e($o['skill']) ?></td>
    <td><?= e($o['level']) ?></td>
    <td><?= e($o['status']) ?></td>
    <td>
      <a href="<?= url('offers/edit?id=' . (int)$o['id']) ?>">Edit</a>
      <form method="post" action="<?= url('offers/delete') ?>" class="inline-form"
            onsubmit="return confirm('Delete this offer?')">
        <?= csrf_field() ?>
        <input type="hidden" name="id" value="<?= (int)$o['id'] ?>">
        <button type="submit">Delete</button>
      </form>
    </td>
  </tr>
  <?php endforeach; ?>
</table>

<h2>People who booked me (I teach)</h2>
<table class="table">
  <tr><th>Learner</th><th>Skill</th><th>When</th><th>Status</th><th>Action</th></tr>
  <?php foreach ($asTeacher as $s): ?>
  <tr>
    <td><?= e($s['learner_name']) ?></td>
    <td><?= e($s['title']) ?></td>
    <td><?= $s['scheduled_at'] ? e($s['scheduled_at']) : '&mdash;' ?></td>
    <td><?= e($s['status']) ?></td>
    <td>
      <?php if ($s['status'] === 'pending'): ?>
        <?= action_btn($s['id'], 'accept', 'Accept') ?>
        <?= action_btn($s['id'], 'cancel', 'Decline') ?>
      <?php elseif ($s['status'] === 'accepted'): ?>
        <?= action_btn($s['id'], 'complete', 'Mark completed (+1)') ?>
      <?php else: ?>&mdash;<?php endif; ?>
    </td>
  </tr>
  <?php endforeach; ?>
</table>

<h2>My bookings (I learn)</h2>
<table class="table">
  <tr><th>Teacher</th><th>Skill</th><th>When</th><th>Status</th><th>Action</th></tr>
  <?php foreach ($asLearner as $s): ?>
  <tr>
    <td><?= e($s['teacher_name']) ?></td>
    <td><?= e($s['title']) ?></td>
    <td><?= $s['scheduled_at'] ? e($s['scheduled_at']) : '&mdash;' ?></td>
    <td><?= e($s['status']) ?></td>
    <td>
      <?php if (in_array($s['status'], ['pending', 'accepted'])): ?>
        <?= action_btn($s['id'], 'cancel', 'Cancel') ?>
      <?php elseif ($s['status'] === 'completed' && !$s['review_id']): ?>
        <a href="<?= url('sessions/review?id=' . (int)$s['id']) ?>">Leave review</a>
      <?php else: ?>&mdash;<?php endif; ?>
    </td>
  </tr>
  <?php endforeach; ?>
</table>
