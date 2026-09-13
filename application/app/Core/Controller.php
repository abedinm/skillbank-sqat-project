<?php
// Base controller. Gives every controller a view() method that wraps a view file
// in the shared header/footer layout, and a partial() for layout-less output
// (used by the AJAX search endpoint).
abstract class Controller
{
    protected function view($name, $data = [])
    {
        extract($data);                       // turn $data keys into variables
        require APP . '/Views/layouts/header.php';
        require APP . '/Views/' . $name . '.php';
        require APP . '/Views/layouts/footer.php';
    }

    protected function partial($name, $data = [])
    {
        extract($data);
        require APP . '/Views/' . $name . '.php';
    }
}
