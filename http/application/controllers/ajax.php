<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

class Ajax extends CI_Controller
{
    public function get_article_suggestion()
    {
        $json_output = array();
        
        $query = trim(str_replace(" ", "_", $this->input->get("query")));
        
        $this->load->model("common_model");
        
        $articles = $this->common_model->get_all_articles_id_containing($query);
        
        if(!empty($articles))
        {            
            foreach($articles as $article)
                
                array_push(
                        $json_output,
                        array(
                            "url" => $article["_id"],
                            "host" => $this->common_model->resolve_article_host($article["_id"]),
                            "title" => $this->common_model->resolve_article_title($article["_id"])
                        )
                );
        }
        
        $json_output = json_encode($json_output);
        
        $this->load->view("json_output", array("json_output" => $json_output));
    }
}

/* End of file ajax.php */
/* Location: ./application/controllers/ajax.php */