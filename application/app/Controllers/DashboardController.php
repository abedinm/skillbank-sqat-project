<?php
class DashboardController extends Controller
{
    // GET /dashboard
    public function index()
    {
        require_login();
        $me = current_user();
        $this->view('dashboard/index', [
            'me'        => $me,
            'myOffers'  => Offer::forUser($me['id']),
            'asTeacher' => SessionModel::forTeacher($me['id']),
            'asLearner' => SessionModel::forLearner($me['id']),
            'wishes'    => Wish::forUser($me['id']),
            'allSkills' => Skill::all(),
            'matches'   => Wish::mutualMatches($me['id']),
        ]);
    }

    // POST /dashboard  -> add/remove wishlist items
    public function wishlist()
    {
        require_login();
        verify_csrf();
        $me = current_user();
        if (isset($_POST['add_wish'])) {
            Wish::add($me['id'], (int)$_POST['skill_id']);
            set_flash('Added to your learning wishlist.');
        } elseif (isset($_POST['remove_wish'])) {
            Wish::remove((int)$_POST['wish_id'], $me['id']);
            set_flash('Removed from wishlist.');
        }
        redirect('dashboard');
    }
}
