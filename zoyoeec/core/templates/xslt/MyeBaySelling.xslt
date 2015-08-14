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
         <th>notes</th>
       </tr>
     </thead>
     <tbody>
 <xsl:for-each select="//ebay:Item"> 
       <tr>
        <td>
          <input>
          <xsl:attribute name='type'>checkbox</xsl:attribute>
          <xsl:attribute name='name'><xsl:value-of select='ebay:ItemID'/></xsl:attribute>
          </input>
        </td>
        <td><a><xsl:attribute name="href"><xsl:value-of select='ebay:ListingDetails/ebay:ViewItemURL'/></xsl:attribute><xsl:value-of select='ebay:Title'/></a></td>
        <td><xsl:value-of select='ebay:ItemID'/></td>
        <td><xsl:attribute name="id"><xsl:value-of select='ebay:ItemID'/></xsl:attribute><xsl:value-of select='ebay:SKU'/></td>
       </tr>
 </xsl:for-each>
    </tbody>
   </table>
 </div>
</div>
</xsl:template>
</xsl:stylesheet>
