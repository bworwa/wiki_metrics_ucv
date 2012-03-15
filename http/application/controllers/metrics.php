<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

class Metrics extends CI_Controller
{
    var $header_data;
    var $body_data;
    var $footer_data;
    
    var $base_url;
    
    var $normalized_article_url;
    
    public function __construct()
    {
        parent::__construct();
        
        $this->header_data = array();
        $this->body_data = array();
        $this->footer_data = array();
        
        $this->body_data["article_url"] = trim($this->input->get("url"));
        
        if(empty($this->body_data["article_url"]))
            header("Location: " . $this->header_data["base_url"] . "index.php");

        $this->load->helper("url");
        $this->base_url = base_url();
        $this->header_data["base_url"] = $this->base_url;
        
        $this->load->model("common_model");
        
        $this->header_data["recent_searches"] = $this->common_model->get_recent_searches($this->base_url);
        
        $this->body_data["article_title"] = $this->common_model->resolve_article_title($this->body_data["article_url"]);
        $this->body_data["article_host"] = $this->common_model->resolve_article_host($this->body_data["article_url"]);
        
        $this->normalized_article_url = $this->common_model->normalize_article_url(parse_url($this->body_data["article_url"]));
    }

    public function index()
    {
        $this->common_model->update_recent_searches_cookies($this->body_data["article_url"]);
        
        $this->header_data["page_title"] = $this->body_data["article_title"];
        
        $article = $this->common_model->get_article_by_id($this->normalized_article_url);

        if (!empty($article))
        {
            $this->load->model("metrics_model");

            $this->body_data["metrics"] = $this->metrics_model->get_metrics($this->normalized_article_url);
        }

        $this->load->view("header", $this->header_data);
        $this->load->view("metrics", $this->body_data);
        $this->load->view("footer", $this->footer_data);
    }

}

/* End of file metrics.php */
/* Location: ./application/controllers/metrics.php */