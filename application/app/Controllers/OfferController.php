<?php
class OfferController extends Controller
{
    // GET /  -> browse all active offers
    public function index()
    {
        $this->view('offers/index', ['offers' => Offer::active()]);
    }

    // GET /search?q=...  -> AJAX endpoint: returns just the cards (no layout)
    public function search()
    {
        $offers = Offer::search($_GET['q'] ?? '');
        if (!$offers) {
            echo '<p>No matching skills found.</p>';
            return;
        }
        foreach ($offers as $offer) {
            $this->partial('offers/_card', ['offer' => $offer]);
        }
    }

    // GET /offer?id=...  -> single offer + reviews
    public function show()
    {
        $offer = Offer::find((int)($_GET['id'] ?? 0));
        if (!$offer) {
            set_flash('Offer not found.');
            redirect('');
        }
        $this->view('offers/show', [
            'offer'   => $offer,
            'summary' => Review::summaryForOffer($offer['id']),
            'reviews' => Review::listForOffer($offer['id']),
        ]);
    }

    // GET /offers/create
    public function createForm()
    {
        require_login();
        $this->view('offers/create', ['skills' => Skill::all()]);
    }

    // POST /offers/create
    public function store()
    {
        require_login();
        verify_csrf();
        $me = current_user();
        $errors = [];
        $skillId = (int)($_POST['skill_id'] ?? 0);
        $title   = trim($_POST['title'] ?? '');

        if (!$skillId)    $errors[] = 'Choose a skill.';
        if ($title === '') $errors[] = 'Title is required.';

        if ($errors) {
            $this->view('offers/create', ['skills' => Skill::all(), 'errors' => $errors]);
            return;
        }
        Offer::create($me['id'], $skillId, $title,
            trim($_POST['description'] ?? ''), $_POST['level'] ?? 'Beginner');
        set_flash('Offer created.');
        redirect('dashboard');
    }

    // GET /offers/edit?id=...
    public function editForm()
    {
        require_login();
        $me = current_user();
        $offer = Offer::findOwned((int)($_GET['id'] ?? 0), $me['id']);
        if (!$offer) {
            set_flash('Offer not found or not yours.');
            redirect('dashboard');
        }
        $this->view('offers/edit', ['offer' => $offer, 'skills' => Skill::all()]);
    }

    // POST /offers/edit?id=...
    public function update()
    {
        require_login();
        verify_csrf();
        $me = current_user();
        $id = (int)($_GET['id'] ?? 0);
        if (!Offer::findOwned($id, $me['id'])) {
            set_flash('Offer not found or not yours.');
            redirect('dashboard');
        }
        Offer::update($id, $me['id'], (int)$_POST['skill_id'], trim($_POST['title']),
            trim($_POST['description']), $_POST['level'], $_POST['status']);
        set_flash('Offer updated.');
        redirect('dashboard');
    }

    // POST /offers/delete
    public function destroy()
    {
        require_login();
        verify_csrf();
        $me = current_user();
        Offer::delete((int)($_POST['id'] ?? 0), $me['id']);
        set_flash('Offer deleted.');
        redirect('dashboard');
    }
}
