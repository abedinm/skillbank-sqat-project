<?php
class AdminController extends Controller
{
    public function index()
    {
        require_admin();
        $this->view('admin/index', [
            'userCount'    => User::count(),
            'offerCount'   => Offer::count(),
            'sessionCount' => (int) Database::scalar(
                                "SELECT COUNT(*) FROM sessions WHERE status = 'completed'"),
            'users'        => User::all(),
        ]);
    }

    public function skills()
    {
        require_admin();
        $this->view('admin/skills', ['skills' => Skill::all()]);
    }

    public function skillsPost()
    {
        require_admin();
        verify_csrf();
        if (isset($_POST['add'])) {
            $name = trim($_POST['name'] ?? '');
            if ($name !== '') {
                Skill::create($name, trim($_POST['category'] ?? '') ?: 'General');
                set_flash('Skill added.');
            }
        } elseif (isset($_POST['delete'])) {
            Skill::delete((int)$_POST['skill_id']);
            set_flash('Skill deleted.');
        }
        redirect('admin/skills');
    }
}
