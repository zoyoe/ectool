{% load template_filters %}
zoyoe.config.data.{{category}} = {};
{% for line in category|shopinfo %}
zoyoe.config.data.{{category}}['{{line.name}}'] = {content:'{{line.content}}',category:'{{line.type}}',datatype:'string'};
{% endfor %}
