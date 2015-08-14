<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ebay="urn:ebay:apis:eBLBaseComponents"
  xmlns:xs ="http://www.w3.org/2001/XMLSchema">
<xsl:template match="/">
 <xsl:for-each select="//ebay:Item"> 
  <div class='ebay-details'>
   <div class='grid_4'>
   <img>
    <xsl:attribute name='src'>
     <xsl:value-of select='ebay:PictureDetails/ebay:GalleryURL'/>
    </xsl:attribute>
   </img>
   </div>
   <div class='grid_8'>
   <ul>
    <li><label>title:</label>
      <input name='title'>
       <xsl:attribute name='value'>
       <xsl:value-of select='ebay:Title'/>
       </xsl:attribute>
      </input>
    </li>
    <li><label>quantity:</label>
      <input name='quantity'>
       <xsl:attribute name='value'>
       <xsl:value-of select='ebay:Quantity'/>
       </xsl:attribute>
      </input>
    </li>
   </ul>
   </div>
  </div>
 </xsl:for-each>
</xsl:template>
</xsl:stylesheet>
