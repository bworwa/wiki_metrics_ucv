<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

class Welcome extends CI_Controller
{
    var $base_url;
    
    var $header_data;
    var $body_data;
    var $footer_data;
    
    var $recent_searches;

    public function __construct()
    {
        parent::__construct();

        $this->header_data = array();
        $this->body_data = array();
        $this->footer_data = array();

        $this->load->helper('url');
        $this->base_url = base_url();
        $this->header_data["base_url"] = $this->base_url;
        
        $this->load->model("common_model");
        $this->header_data["recent_searches"] = $this->common_model->get_recent_searches($this->base_url);
    }

    public function index()
    {
        $this->header_data["page_title"] = "Wiki-Metrics-UCV";

        $this->load->view('header', $this->header_data);
        $this->load->view('welcome', $this->body_data);
        $this->load->view('footer', $this->footer_data);
    }

    public function view_all_articles()
    {
        $this->header_data["page_title"] = "Wiki-Metrics-UCV";

        $articles = $this->common_model->get_all_articles_id();

        $this->body_data["articles"] = array();

        if (!empty($articles))            
            foreach ($articles as $article)                
                array_push(
                        $this->body_data["articles"],
                        array(
                            "url" => urlencode($article["_id"]),
                            "host" => $this->common_model->resolve_article_host($article["_id"]),
                            "title" => $this->common_model->resolve_article_title($article["_id"])
                        )
                );
        
        usort($this->body_data["articles"], function($first_element, $second_element)
                {
                    return $first_element["title"] > $second_element["title"];
                });

        $this->load->view('header', $this->header_data);
        $this->load->view('view_all_articles', $this->body_data);
        $this->load->view('footer', $this->footer_data);
    }
}

/* End of file welcome.php */
/* Location: ./application/controllers/welcome.php */