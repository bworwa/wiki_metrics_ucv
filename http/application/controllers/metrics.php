<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Metrics extends CI_Controller
{
	public function index()
	{
		$header_data = array();

		$metrics_data = array();

		$this->load->helper('url');

		$header_data["base_url"] = base_url();

		$article_url = trim($this->input->get("url"));

		$parsed_article_url = parse_url($article_url);

		parse_str($parsed_article_url["query"], $query_string);

		$header_data["article_title"] = str_replace("_", " ", $query_string["title"]);

		$query_string["title"] = urldecode($query_string["title"]);

		$article_url = 
			$parsed_article_url["scheme"] .
			"://" .
			$parsed_article_url["host"] .
			$parsed_article_url["path"] .
			"?" .
			http_build_query($query_string);

		if(empty($article_url))

			header("Location: " . $header_data["base_url"] . "index.php");

		$mongo = new Mongo();

		$db = $mongo->wiki_metrics_ucv;

		$article = $db->articles->findOne(array("_id" => $article_url));		

		if(empty($article))

			# TODO
			;

		else
		{
			$revisions_count = $db->histories->group(
				array("date" => 1),
				array("revisions" => 0),
				"function(obj, prev){ prev.revisions += 1; }",
				array("article" => $article_url)
			);

			$metrics_data["revisions_count"] = $revisions_count["retval"];

			parse_str(parse_url($article_url, PHP_URL_QUERY), $query_string);
		}

		$this->load->view('header', $header_data);

		$this->load->view('metrics', $metrics_data);

		$this->load->view('footer');
	}
}

/* End of file metrics.php */
/* Location: ./application/controllers/metrics.php */
