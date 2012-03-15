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
                
                if(obj.user.match(/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/))
                    if(typeof prev.metrics['users_related_metrics']['[Other]'] != 'undefined')
                        prev.metrics['users_related_metrics']['[Other]'] += 1;
                    else
                        prev.metrics['users_related_metrics']['[Other]'] = 1;
                else
                    if(typeof prev.metrics['users_related_metrics'][obj.user] != 'undefined')
                        prev.metrics['users_related_metrics'][obj.user] += 1;
                    else
                        prev.metrics['users_related_metrics'][obj.user] = 1;
            }",
            array("article" => $article_id)
        );

        $metrics = $metrics["retval"][0]["metrics"];

        usort(
                $metrics["date_related_metrics"],
                function($first_element, $second_element)
                {
                    return $first_element["timestamp"] > $second_element["timestamp"];
                }
        );       

        return $metrics;
    }
}

/* End of file metrics_model.php */
/* Location: ./application/models/metrics_model.php */