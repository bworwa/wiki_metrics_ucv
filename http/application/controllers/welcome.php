<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Welcome extends CI_Controller
{
	public function index()
	{
		$header_data = array();

		$this->load->helper('url');

		$header_data["base_url"] = base_url();

		$header_data["welcome_title"] = "Wiki-Metrics-UCV";

		$this->load->view('header', $header_data);

		$this->load->view('welcome');

		$this->load->view('footer');
	}
}

/* End of file welcome.php */
/* Location: ./application/controllers/welcome.php */
