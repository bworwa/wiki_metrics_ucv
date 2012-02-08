<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Metrics extends CI_Controller
{
	public function index()
	{
		$header_data = array();

		$metrics_data = array();

		$this->load->helper('url');

		$header_data["base_url"] = base_url();

		$metrics_data["article_url"] = trim($this->input->get("url"));

		$parsed_article_url = parse_url($metrics_data["article_url"]);

		parse_str($parsed_article_url["query"], $query_string);

		$header_data["article_title"] = str_replace("_", " ", $query_string["title"]);

		$query_string["title"] = urldecode($query_string["title"]);

		$metrics_data["article_url"] = 
			$parsed_article_url["scheme"] .
			"://" .
			$parsed_article_url["host"] .
			$parsed_article_url["path"] .
			"?" .
			http_build_query($query_string);

		if(empty($metrics_data["article_url"]))

			header("Location: " . $header_data["base_url"] . "index.php");

		$mongo = new Mongo();

		$db = $mongo->wiki_metrics_ucv;

		$article = $db->articles->findOne(array("_id" => $metrics_data["article_url"]));		

		if(empty($article))

			# TODO
			;

		else
		{
			$revisions_count = $db->histories->group(
				array(),
				array("revisions" => array()),
				"function(obj, prev){
					var date = new Date(obj.date * 1000);
					var dateKey = hex_md5(date.getFullYear() + '' + date.getMonth());
					if(typeof prev.revisions[dateKey] != 'undefined')
						prev.revisions[dateKey]['revisions'] += 1;
					else
					{
						prev.revisions[dateKey] = Array();
						prev.revisions[dateKey]['timestamp'] = date;
						prev.revisions[dateKey]['date'] = (date.getMonth() + 1) + '/' + date.getFullYear();
						prev.revisions[dateKey]['revisions'] = 1;
					}
				}",
				array("article" => $metrics_data["article_url"])
			);

			$metrics_data["revisions_count"] = $revisions_count["retval"][0]["revisions"];

			usort($metrics_data["revisions_count"], function($first_element, $second_element) {
				return $first_element["timestamp"]->sec > $second_element["timestamp"]->sec;
			});
		}

		$this->load->view('header', $header_data);

		$this->load->view('metrics', $metrics_data);

		$this->load->view('footer');
	}
}

/* End of file metrics.php */
/* Location: ./application/controllers/metrics.php */
