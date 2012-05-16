<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

class Metrics_Model extends CI_Model
{
    var $mongo;
    var $db;

    function Metrics_Model()
    {
        $this->mongo = new Mongo();
        $this->db = $this->mongo->wiki_metrics_ucv;
    }

    function get_metrics($article_id)
    {
        $metrics = $this->db->histories->group(
            array(),
            array("metrics" => array( "date_related_metrics" => array(), "users_related_metrics" => array())),
            "function(obj, prev)
            {
                var date = new Date(obj.date * 1000);
                var dateKey = hex_md5(date.getFullYear() + '' + date.getMonth());
                                                
                if(typeof prev.metrics['date_related_metrics'][dateKey] != 'undefined')
                {
                    prev.metrics['date_related_metrics'][dateKey]['total_revisions'] += 1;
                    if(obj.minor === true)
                        prev.metrics['date_related_metrics'][dateKey]['minor_revisions'] += 1;
                        
                    if(obj.size < prev.metrics['date_related_metrics'][dateKey]['min_size'])
                        prev.metrics['date_related_metrics'][dateKey]['min_size'] = obj.size;
                    if(obj.size > prev.metrics['date_related_metrics'][dateKey]['min_size'])
                        prev.metrics['date_related_metrics'][dateKey]['max_size'] = obj.size;
                    prev.metrics['date_related_metrics'][dateKey]['avg_size'] = (prev.metrics['date_related_metrics'][dateKey]['min_size'] + prev.metrics['date_related_metrics'][dateKey]['max_size']) / 2;
                }
                else
                {
                    prev.metrics['date_related_metrics'][dateKey] = Array();
                    
                    prev.metrics['date_related_metrics'][dateKey]['timestamp'] = obj.date;
                    
                    prev.metrics['date_related_metrics'][dateKey]['date'] = (date.getMonth() + 1) + '/' + date.getFullYear();
                    
                    prev.metrics['date_related_metrics'][dateKey]['total_revisions'] = 1;
                    if(obj.minor === true)
                        prev.metrics['date_related_metrics'][dateKey]['minor_revisions'] = 1;
                    else
                        prev.metrics['date_related_metrics'][dateKey]['minor_revisions'] = 0;
                        
                    prev.metrics['date_related_metrics'][dateKey]['min_size'] = obj.size;
                    prev.metrics['date_related_metrics'][dateKey]['max_size'] = obj.size;
                    prev.metrics['date_related_metrics'][dateKey]['avg_size'] = (prev.metrics['date_related_metrics'][dateKey]['min_size'] + prev.metrics['date_related_metrics'][dateKey]['max_size']) / 2;           
                }
                

                if(typeof prev.metrics['users_related_metrics'][obj.user] != 'undefined')
                {
                    if(obj.minor && typeof prev.metrics['users_related_metrics'][obj.user]['minor_revisions'] != 'undefined')
                        prev.metrics['users_related_metrics'][obj.user]['minor_revisions'] += 1;
                    else if(obj.minor && typeof prev.metrics['users_related_metrics'][obj.user]['minor_revisions'] == 'undefined')
                        prev.metrics['users_related_metrics'][obj.user]['minor_revisions'] = 1;
                        
                    if(typeof prev.metrics['users_related_metrics'][obj.user]['total_revisions'] != 'undefined')
                        prev.metrics['users_related_metrics'][obj.user]['total_revisions'] += 1;
                    else
                        prev.metrics['users_related_metrics'][obj.user]['total_revisions'] = 1;
                }
                else
                {
                    prev.metrics['users_related_metrics'][obj.user] = Array();
                        
                    if(obj.minor && typeof prev.metrics['users_related_metrics'][obj.user]['minor_revisions'] != 'undefined')
                        prev.metrics['users_related_metrics'][obj.user]['minor_revisions'] += 1;
                    else if(obj.minor && typeof prev.metrics['users_related_metrics'][obj.user]['minor_revisions'] == 'undefined')
                        prev.metrics['users_related_metrics'][obj.user]['minor_revisions'] = 1;
                        
                    if(typeof prev.metrics['users_related_metrics'][obj.user]['total_revisions'] != 'undefined')
                        prev.metrics['users_related_metrics'][obj.user]['total_revisions'] += 1;
                    else
                        prev.metrics['users_related_metrics'][obj.user]['total_revisions'] = 1;
                }
            }",
            array("article" => $article_id)
        );

        if(!empty($metrics["retval"][0]["metrics"]))
        {
            $metrics = $metrics = $metrics["retval"][0]["metrics"];
            
            usort(
                    $metrics["date_related_metrics"],
                    function($first_element, $second_element)
                    {
                        return $first_element["timestamp"] > $second_element["timestamp"];
                    }
            );

            foreach($metrics["users_related_metrics"] as &$metric)
            {
                if(!(array_key_exists("total_revisions", $metric)))
                    $metric["total_revisions"] = 0;
                if(!(array_key_exists("minor_revisions", $metric)))
                    $metric["minor_revisions"] = 0;
            }

            uasort(
                    $metrics["users_related_metrics"],
                    function($first_element, $second_element)
                    {                    
                        return $first_element["total_revisions"] < $second_element["total_revisions"];
                    }
            );
        }
        else
        {
            $metrics = null;
        }
        
        return $metrics;
    }
}

/* End of file metrics_model.php */
/* Location: ./application/models/metrics_model.php */
