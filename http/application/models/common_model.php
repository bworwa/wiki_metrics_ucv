<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

class Common_Model extends CI_Model
{
    var $mongo;
    var $db;
    
    var $recent_searches_cookie = "recent_searches";

    public function Common_Model()
    {
        $this->mongo = new Mongo();
        $this->db = $this->mongo->wiki_metrics_ucv;
        
        $this->load->helper("cookie");
    }
    
    public function normalize_article_url($url_fragments)
    {
        $query_string = array();
        
        if(!empty($url_fragments["query"]))
        {
            parse_str($url_fragments["query"], $query_string);
            
            $url_fragments["query"] = http_build_query($query_string);
        }
        
        return ((!empty($url_fragments["scheme"])) ? $url_fragments["scheme"] . "://" : "")
            .((!empty($url_fragments["user"])) ? $url_fragments["user"] . ((!empty($url_fragments["pass"])) ? ":" . $url_fragments["pass"] : "") ."@" : "")
            .((!empty($url_fragments["host"])) ? $url_fragments["host"] : "")
            .((!empty($url_fragments["port"])) ? ":" . $url_fragments["port"] : "")
            .((!empty($url_fragments["path"])) ? $url_fragments["path"] : "")
            .((!empty($url_fragments["query"])) ? "?" . $url_fragments["query"] : "")
            .((!empty($url_fragments["fragment"])) ? "#" . $url_fragments["fragment"] : "");
    }

    public function resolve_article_title($article_url)
    {
        $parsed_article_url = parse_url($article_url);

        $query_string = array();

        parse_str($parsed_article_url["query"], $query_string);

        return str_replace("_", " ", $query_string["title"]);
    }
    
    public function resolve_article_host($article_url)
    {
        return parse_url($article_url, PHP_URL_HOST);
    }

    public function get_all_articles_id()
    {
        $articles = $this->db->articles->find(array(), array("_id" => 1));

        if ($articles->count() > 0)
            /* @var $articles MongoCursor */
            return $articles;

        return null;
    }

    public function get_all_articles_id_containing($pattern)
    {
        if (!empty($pattern))
        {
            $articles = $this->db->articles->find(array("_id" => new MongoRegex("/title=$pattern.*/i")), array("_id" => 1));

            if ($articles->count() > 0)
                /* @var $articles MongoCursor */
                return $articles;
        }

        return null;
    }
    
    public function get_article_by_id($id)
    {
        $article = $this->db->articles->findOne(array("_id" => $id));

        if (!empty($article))
            /* @var $article MongoCursor */
            return $article;
        
        return null;
    }
    
    private function delete_recent_searches_cookies()
    {
        delete_cookie($this->recent_searches_cookie);
    }
    
    public function update_recent_searches_cookies($article_url)
    {        
        $recent_searches = $this->input->cookie($this->recent_searches_cookie);
        
        if(!empty($recent_searches))
        {
            if(strpos($recent_searches, $article_url) === FALSE)
            {
                if(substr_count($recent_searches, ",") === 3)                        
                    $cookie_content = $article_url . "," . substr($recent_searches, 0, strrpos($recent_searches, ","));
                else
                    $cookie_content = $article_url . "," . $recent_searches;
                
                $cookie = array(
                    "name"   => $this->recent_searches_cookie,
                    "value"  => $cookie_content,
                    "expire" => "2629744",
                );

                set_cookie($cookie);
            }
        }
        else
        {
            $cookie = array(
                "name"   => $this->recent_searches_cookie,
                "value"  => $article_url,
                "expire" => "2629744",
            );
            
            set_cookie($cookie);
        }
    }
    
    public function get_recent_searches($base_url)
    {
        $recent_searches = get_cookie($this->recent_searches_cookie);

        if(!empty($recent_searches))
        {
            $recently_searched_articles = "";

            foreach(explode(",", $recent_searches) as $recent_search)
            {
                $recently_searched_articles .= "<a href=\"" . $base_url. "index.php/metrics?url=" . urlencode($recent_search) . "\">" . $this->common_model->resolve_article_title($recent_search) . "</a>, ";
            }

            return rtrim($recently_searched_articles, ", ");
        }
        else
        {
            return "none";
        }
    }
}

/* End of file common_model.php */
/* Location: ./application/models/common_model.php */