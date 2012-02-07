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

	public function view_all_articles()
	{
		$this->load->helper('url');

		$mongo = new Mongo();

		$db = $mongo->wiki_metrics_ucv;

		$articles = $db->articles->find(array(), array("_id" => 1));

		header("Content-type: text/html; charset=utf-8");

		echo "<ul>";

		foreach($articles as $article)
		{
			$parsed_article_url = parse_url($article["_id"]);

			parse_str($parsed_article_url["query"], $query_string);

			echo "<li>
					<a href=\"" .base_url() ."index.php/metrics?url=" . urlencode($article["_id"]) ."\">" .
						str_replace("_", " ", $query_string["title"]) .
					"</a>
				</li>";
		}

		echo "</ul>";
	}
}

/* End of file welcome.php */
/* Location: ./application/controllers/welcome.php */
