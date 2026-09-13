<?php
class SessionController extends Controller
{
    // POST /sessions/request  -> learner books an offer
    public function request()
    {
        require_login();
        verify_csrf();
        $me = current_user();
        $offer = Offer::find((int)($_POST['offer_id'] ?? 0));
        if (!$offer) {
            set_flash('Offer not found.');
            redirect('');
        }
        $scheduled = trim($_POST['scheduled_at'] ?? '');
        $scheduled = $scheduled !== '' ? str_replace('T', ' ', $scheduled) . ':00' : null;

        if ($me['id'] == $offer['teacher_id']) {
            set_flash("You can't book your own offer.");
        } elseif ($me['credits'] < 1) {
            set_flash('You need at least 1 credit. Teach someone first to earn one.');
        } else {
            SessionModel::create($me['id'], $offer['teacher_id'], $offer['id'], $scheduled);
            set_flash('Request sent! The teacher will accept it.');
        }
        redirect('offer?id=' . $offer['id']);
    }

    // POST /sessions/action  -> accept / complete / cancel
    public function action()
    {
        require_login();
        verify_csrf();
        $me = current_user();
        $session = SessionModel::find((int)($_POST['id'] ?? 0));
        $action  = $_POST['action'] ?? '';
        if (!$session) {
            set_flash('Session not found.');
            redirect('dashboard');
        }
        $isTeacher = ($me['id'] == $session['teacher_id']);
        $isLearner = ($me['id'] == $session['learner_id']);

        if ($action === 'accept' && $isTeacher && $session['status'] === 'pending') {
            SessionModel::setStatus($session['id'], 'accepted');
            set_flash('Session accepted.');
        } elseif ($action === 'complete' && $isTeacher && $session['status'] === 'accepted') {
            $this->completeWithTransfer($session);
        } elseif ($action === 'cancel' && ($isTeacher || $isLearner)
                  && in_array($session['status'], ['pending', 'accepted'])) {
            SessionModel::setStatus($session['id'], 'cancelled');
            set_flash('Session cancelled.');
        } else {
            set_flash('That action is not allowed.');
        }
        redirect('dashboard');
    }

    // The signature feature: move 1 credit learner -> teacher atomically.
    private function completeWithTransfer($session)
    {
        if (User::credits($session['learner_id']) < 1) {
            set_flash('Cannot complete: the learner has no credits left.');
            return;
        }
        $conn = Database::conn();
        mysqli_begin_transaction($conn);
        try {
            User::changeCredits($session['learner_id'], -1);
            User::changeCredits($session['teacher_id'], +1);
            Transaction::record($session['learner_id'], $session['teacher_id'], $session['id']);
            SessionModel::setStatus($session['id'], 'completed');
            mysqli_commit($conn);
            set_flash('Session completed. 1 credit transferred to you.');
        } catch (Exception $ex) {
            mysqli_rollback($conn);
            set_flash('Something went wrong; no credits were changed.');
        }
    }

    // GET /sessions/review?id=...
    public function reviewForm()
    {
        require_login();
        $session = $this->reviewableOrRedirect((int)($_GET['id'] ?? 0));
        $offer = Offer::find($session['offer_id']);
        $session['title'] = $offer['title'] ?? 'session';
        $this->view('sessions/review', ['session' => $session]);
    }

    // POST /sessions/review
    public function review()
    {
        require_login();
        verify_csrf();
        $id = (int)($_POST['id'] ?? 0);
        $this->reviewableOrRedirect($id);
        $rating = (int)($_POST['rating'] ?? 0);
        if ($rating < 1 || $rating > 5) {
            set_flash('Rating must be 1 to 5.');
            redirect('sessions/review?id=' . $id);
        }
        Review::create($id, current_user()['id'], $rating, trim($_POST['comment'] ?? ''));
        set_flash('Thanks for your review!');
        redirect('dashboard');
    }

    // Guard: the current user may review only their own completed, unreviewed sessions.
    private function reviewableOrRedirect($id)
    {
        $me = current_user();
        $session = SessionModel::find($id);
        if (!$session || $session['learner_id'] != $me['id']
            || $session['status'] !== 'completed' || Review::forSession($id)) {
            set_flash('You cannot review that session.');
            redirect('dashboard');
        }
        return $session;
    }
}
