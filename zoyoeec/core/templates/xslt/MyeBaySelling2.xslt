<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ebay="urn:ebay:apis:eBLBaseComponents"
  xmlns:xs ="http://www.w3.org/2001/XMLSchema">
<xsl:template match="/">
<div>
 <div class="table-responsive">
   <table class="table table-striped">
     <thead>
       <tr>
         <th>all</th>
         <th>item name</th>
         <th>item id</th>
         <th>time left</th>
         <th>notes</th>
       </tr>
     </thead>
     <tbody>
 <xsl:for-each select="//ebay:ItemArray/ebay:Item"> 
       <tr>
        <td>
          <input>
          <xsl:attribute name='type'>checkbox</xsl:attribute>
          <xsl:attribute name='name'><xsl:value-of select='ebay:ItemID'/></xsl:attribute>
          </input>
        </td>
        <td><a><xsl:attribute name="href"><xsl:value-of select='ebay:ListingDetails/ebay:ViewItemURL'/></xsl:attribute><xsl:value-of select='ebay:Title'/></a></td>
        <td><xsl:value-of select='ebay:ItemID'/></td>
        <td><xsl:value-of select='ebay:TimeLeft'/></td>
        <td><xsl:attribute name="id"><xsl:value-of select='ebay:ItemID'/></xsl:attribute><xsl:value-of select='ebay:SKU'/></td>
       </tr>
 </xsl:for-each>
    </tbody>
   </table>
</div>

<div class="col-xs-6">
 <div class="dataTables_paginate paging_simple_numbers" id="dataTable_paginate">
 <ul class="pagination">
 <li class="paginate_button previous disabled" aria-controls="dataTable" tabindex="0" id="dataTable_previous"><a href="#">Previous</a></li>
 {% for page in pages %}
 <li class="paginate_button" aria-controls="dataTable" tabindex="0"><a href="/admin/deploy/?page={{page}}">{{page}}</a></li>
 {% endfor %}
 <li class="paginate_button next" aria-controls="dataTable" tabindex="0" id="dataTable_next"><a href="#">Next</a></li>
 </ul>
 </div>
</div>
</div>

</xsl:template>
</xsl:stylesheet>

